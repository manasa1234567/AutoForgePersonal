"""Build reviewed source in ACR and deploy it to an isolated Container App."""
from __future__ import annotations

import asyncio
import base64
import hashlib
import io
import os
import re
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable
from urllib.parse import quote

import httpx

from ..models.schemas import BuildState

Progress = Callable[[str, str], Awaitable[None]]
ARM = "https://management.azure.com"
ACR_API_VERSION = "2019-04-01"
ACA_API_VERSION = "2025-07-01"


@dataclass(frozen=True)
class DirectDeployment:
    url: str
    app_name: str
    image: str
    acr_run_id: str


class AzureDirectDeployer:
    """Deploy without publishing the project to a GitHub feature branch.

    ACR Tasks receives the source archive and Dockerfile, builds/pushes the
    image, and ARM creates the per-build Container App. The app is only marked
    deployed after its public HTTPS endpoint returns HTTP 200.
    """

    @staticmethod
    def configured() -> bool:
        required = (
            "AZURE_SUBSCRIPTION_ID", "ACA_RESOURCE_GROUP", "ACA_ENVIRONMENT_NAME",
            "ACR_LOGIN_SERVER", "ACA_REGISTRY_IDENTITY",
        )
        identity_mode = os.getenv("AUTOFORGE_IDENTITY_MODE", "").strip().lower()
        return (
            os.getenv("AUTOFORGE_AZURE_DIRECT_DEPLOYMENT_ENABLED", "false").strip().lower() == "true"
            and os.getenv("AUTOFORGE_DEPLOYMENT_ENABLED", "false").strip().lower() == "true"
            and identity_mode == "managed_identity"
            and all(os.getenv(name, "").strip() for name in required)
        )

    def __init__(self) -> None:
        if not self.configured():
            raise RuntimeError(
                "Direct Azure deployment is not configured. Enable AUTOFORGE_AZURE_DIRECT_DEPLOYMENT_ENABLED, "
                "use the managed identity, and configure the Azure subscription, Container Apps environment, "
                "ACR login server, and ACA_REGISTRY_IDENTITY resource ID."
            )
        self.subscription = os.environ["AZURE_SUBSCRIPTION_ID"].strip()
        self.resource_group = os.environ["ACA_RESOURCE_GROUP"].strip()
        self.acr_resource_group = os.getenv("ACR_RESOURCE_GROUP", os.getenv("AZURE_RESOURCE_GROUP", self.resource_group)).strip()
        self.environment = os.environ["ACA_ENVIRONMENT_NAME"].strip()
        self.registry_server = os.environ["ACR_LOGIN_SERVER"].strip().rstrip("/")
        self.registry_name = os.getenv("ACR_NAME", self.registry_server.split(".", 1)[0]).strip()
        self.registry_identity = os.environ["ACA_REGISTRY_IDENTITY"].strip()
        if not re.fullmatch(r"[a-z0-9]+\.azurecr\.io", self.registry_server):
            raise RuntimeError("ACR_LOGIN_SERVER must be the login server of an Azure Container Registry.")
        if not self.registry_identity.startswith("/subscriptions/"):
            raise RuntimeError("ACA_REGISTRY_IDENTITY must be the resource ID of the user-assigned registry identity.")
        self.timeout = httpx.Timeout(connect=20, read=60, write=120, pool=20)

    async def deploy(self, build: BuildState, progress: Progress) -> DirectDeployment:
        artifacts = build.proof.artifacts if build.proof else {}
        if not artifacts:
            raise RuntimeError("Direct Azure deployment stopped: the approved source files are missing.")
        dockerfile = artifacts.get("Dockerfile")
        if not dockerfile:
            raise RuntimeError("Direct Azure deployment requires the generated project root Dockerfile.")
        reserved = {".autoforge.dockerfile", ".autoforge-platform"}
        if any(path.split("/", 1)[0].casefold() in reserved for path in artifacts):
            raise RuntimeError("Generated source uses a reserved AutoForge packaging path; rename it before direct deployment.")
        port = self._port(dockerfile)
        from ..agents.poetry_packaging import resolve_poetry_before_install

        # Build from a disposable context copy. The reviewed source and its
        # manifests remain byte-for-byte unchanged; the build-only Dockerfile
        # refreshes Poetry locks, and the shared npm resolver refreshes npm
        # lockfiles inside a credential-free ACR task.
        staged = dict(artifacts)
        staged[".autoforge.Dockerfile"] = resolve_poetry_before_install(dockerfile)
        npm_resolver = Path(__file__).resolve().parents[1] / "agents" / "resolve_generated_npm_locks.cjs"
        staged[".autoforge-platform/resolve-generated-npm-locks.cjs"] = npm_resolver.read_text(encoding="utf-8")
        ignore = staged.get(".dockerignore", "")
        staged[".dockerignore"] = ignore.rstrip() + "\n.autoforge-platform/\n" if ignore.strip() else ".autoforge-platform/\n"
        archive = self._source_archive(staged)
        digest = hashlib.sha256(archive).hexdigest()[:12]
        app_name = f"af-{re.sub(r'[^a-f0-9]', '', build.id.lower())[:8]}"
        image = f"{self.registry_server}/autoforge-generated:{build.id}-{digest}"

        credential = self._credential()
        try:
            token = await credential.get_token("https://management.azure.com/.default")
            headers = {"Authorization": f"Bearer {token.token}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await progress("Azure source upload", "Uploading approved source directly to Azure Container Registry build service")
                upload = await self._arm(client, "POST", self._acr_url("listBuildSourceUploadUrl"), headers)
                upload_url = upload.get("uploadUrl")
                relative_path = upload.get("relativePath")
                if not upload_url or not relative_path:
                    raise RuntimeError("Azure Container Registry did not return a source upload location.")
                uploaded = await client.put(upload_url, content=archive, headers={"Content-Type": "application/octet-stream"})
                self._require_success(uploaded, "upload the approved source archive")

                await progress("Azure image build", "Building and pushing the generated app image in Azure Container Registry")
                tag = image.rsplit(":", 1)[1]
                task = (
                    "version: v1.1.0\n"
                    "stepTimeout: 6900\n"
                    "workingDirectory: /workspace\n"
                    "steps:\n"
                    "  - cmd: node:22-alpine node /workspace/.autoforge-platform/resolve-generated-npm-locks.cjs /workspace\n"
                    "    timeout: 300\n"
                    f"  - build: -t $Registry/autoforge-generated:{tag} -f .autoforge.Dockerfile .\n"
                    "  - push:\n"
                    f"      - $Registry/autoforge-generated:{tag}\n"
                )
                run = await self._arm(client, "POST", self._acr_url("scheduleRun"), headers, json={
                    "type": "EncodedTaskRunRequest",
                    "sourceLocation": relative_path,
                    "encodedTaskContent": base64.b64encode(task.encode("utf-8")).decode("ascii"),
                    "isArchiveEnabled": True,
                    "timeout": 7200,
                    "platform": {"os": "Linux", "architecture": "amd64"},
                    "agentConfiguration": {"cpu": 2},
                })
                run_id = (run.get("properties") or {}).get("runId") or run.get("name")
                if not run_id:
                    raise RuntimeError("Azure Container Registry did not return the image build run ID.")
                await self._wait_for_acr_run(client, headers, run_id, progress)

                await progress("Azure Container App", f"Creating the isolated Azure app {app_name}")
                env_id, location = await self._environment(client, headers)
                await self._create_app(client, headers, build, app_name, image, env_id, location, port)
                app = await self._wait_for_app(client, headers, app_name)
                fqdn = (((app.get("properties") or {}).get("configuration") or {}).get("ingress") or {}).get("fqdn")
                if not fqdn:
                    raise RuntimeError("Azure Container Apps did not return a public ingress hostname.")
                url = f"https://{fqdn}"
                await progress("Azure smoke test", f"Checking the deployed application at {url}")
                expect_frontend = any(
                    path.lower().endswith("index.html")
                    and not any(part in {"tests", "__tests__", "node_modules"} for part in path.lower().split("/"))
                    for path in artifacts
                )
                await self._smoke_test(client, url, require_html=expect_frontend)
                return DirectDeployment(url=url, app_name=app_name, image=image, acr_run_id=run_id)
        finally:
            await credential.close()

    @staticmethod
    def _credential():
        try:
            from azure.identity.aio import ManagedIdentityCredential
        except ImportError as exc:
            raise RuntimeError("Direct Azure deployment requires azure-identity in the backend image.") from exc
        client_id = os.getenv("AZURE_CLIENT_ID", "").strip()
        return ManagedIdentityCredential(client_id=client_id) if client_id else ManagedIdentityCredential()

    def _acr_url(self, operation: str) -> str:
        return (
            f"{ARM}/subscriptions/{quote(self.subscription, safe='')}/resourceGroups/{quote(self.acr_resource_group, safe='')}"
            f"/providers/Microsoft.ContainerRegistry/registries/{quote(self.registry_name, safe='')}/{operation}"
            f"?api-version={ACR_API_VERSION}"
        )

    @staticmethod
    async def _arm(client: httpx.AsyncClient, method: str, url: str, headers: dict, **kwargs):
        response = await client.request(method, url, headers=headers, **kwargs)
        AzureDirectDeployer._require_success(response, "call the Azure deployment API")
        try:
            return response.json()
        except ValueError:
            return {}

    @staticmethod
    def _require_success(response: httpx.Response, operation: str) -> None:
        if response.is_success:
            return
        detail = ""
        try:
            body = response.json()
            detail = body.get("error", {}).get("message", "") if isinstance(body, dict) else ""
        except ValueError:
            pass
        if detail:
            detail = re.sub(r"https?://\S+", "[Azure URL]", detail)[:700]
        raise RuntimeError(f"Could not {operation} (HTTP {response.status_code})" + (f": {detail}" if detail else "."))

    async def _wait_for_acr_run(self, client, headers, run_id, progress):
        url = f"{self._acr_url('scheduleRun').split('/scheduleRun?', 1)[0]}/runs/{quote(run_id, safe='')}?api-version={ACR_API_VERSION}"
        loop = asyncio.get_running_loop()
        deadline = loop.time() + 7200
        last_report = 0.0
        while loop.time() < deadline:
            result = await self._arm(client, "GET", url, headers)
            props = result.get("properties") or {}
            status = str(props.get("status", "")).lower()
            if status == "succeeded":
                return
            if status in {"failed", "canceled", "timeout", "error"}:
                raise RuntimeError(f"Azure image build {status}; inspect ACR task run {run_id} for its build log.")
            if loop.time() - last_report >= 60:
                await progress("Azure image build", f"Azure Container Registry build is {status or 'running'} (run {run_id})")
                last_report = loop.time()
            await asyncio.sleep(8)
        raise RuntimeError(f"Azure image build timed out after two hours (ACR run {run_id}).")

    async def _environment(self, client, headers):
        url = (
            f"{ARM}/subscriptions/{quote(self.subscription, safe='')}/resourceGroups/{quote(self.resource_group, safe='')}"
            f"/providers/Microsoft.App/managedEnvironments/{quote(self.environment, safe='')}?api-version={ACA_API_VERSION}"
        )
        result = await self._arm(client, "GET", url, headers)
        env_id = result.get("id")
        location = result.get("location")
        if not env_id or not location:
            raise RuntimeError("The configured Azure Container Apps environment has no resource ID or location.")
        return env_id, location

    async def _create_app(self, client, headers, build, app_name, image, env_id, location, port):
        url = (
            f"{ARM}/subscriptions/{quote(self.subscription, safe='')}/resourceGroups/{quote(self.resource_group, safe='')}"
            f"/providers/Microsoft.App/containerApps/{quote(app_name, safe='')}?api-version={ACA_API_VERSION}"
        )
        payload = {
            "location": location,
            "identity": {"type": "UserAssigned", "userAssignedIdentities": {self.registry_identity: {}}},
            "properties": {
                "environmentId": env_id,
                "configuration": {
                    "activeRevisionsMode": "Single",
                    "ingress": {"external": True, "targetPort": port, "transport": "http", "allowInsecure": False},
                    "registries": [{"server": self.registry_server, "identity": self.registry_identity}],
                },
                "template": {
                    "containers": [{
                        "name": "generated-app", "image": image,
                        "resources": {"cpu": 0.5, "memory": "1Gi"},
                        "env": [{"name": "PORT", "value": str(port)}],
                    }],
                    "scale": {"minReplicas": 0, "maxReplicas": 1},
                },
            },
            "tags": {"managed-by": "autoforge", "autoforge-build-id": build.id, "autoforge-deployment-mode": "azure-direct"},
        }
        response = await client.put(url, headers=headers, json=payload)
        self._require_success(response, f"create Azure Container App {app_name}")

    async def _wait_for_app(self, client, headers, app_name):
        url = (
            f"{ARM}/subscriptions/{quote(self.subscription, safe='')}/resourceGroups/{quote(self.resource_group, safe='')}"
            f"/providers/Microsoft.App/containerApps/{quote(app_name, safe='')}?api-version={ACA_API_VERSION}"
        )
        deadline = asyncio.get_running_loop().time() + 900
        while asyncio.get_running_loop().time() < deadline:
            response = await client.get(url, headers=headers)
            if response.status_code == 404:
                await asyncio.sleep(8)
                continue
            self._require_success(response, f"read Azure Container App {app_name}")
            app = response.json()
            state = str((app.get("properties") or {}).get("provisioningState", "")).lower()
            if state == "succeeded":
                return app
            if state in {"failed", "canceled"}:
                raise RuntimeError(f"Azure Container App provisioning {state}.")
            await asyncio.sleep(8)
        raise RuntimeError("Azure Container App provisioning did not finish within 15 minutes.")

    @staticmethod
    async def _smoke_test(client, url, require_html=False):
        for attempt in range(18):
            try:
                response = await client.get(url + "/", timeout=12)
                if response.status_code == 200:
                    if not require_html:
                        return
                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" in content_type and re.search(rb"<!doctype html|<html(?:\s|>)", response.content[:4096], re.I):
                        return
            except httpx.HTTPError:
                pass
            if attempt < 17:
                await asyncio.sleep(5)
        message = "Azure created the app, but its public URL did not return HTTP 200. Check the Container App logs."
        if require_html:
            message = "Azure created the app, but its public URL did not return an HTML page. Check the Container App logs and generated frontend startup."
        raise RuntimeError(message)

    @staticmethod
    def _port(dockerfile: str) -> int:
        ports = re.findall(r"(?im)^\s*EXPOSE\s+([0-9]{1,5})(?:/\w+)?(?:\s|$)", dockerfile)
        if not ports:
            raise RuntimeError("The generated Dockerfile must declare its HTTP port with EXPOSE.")
        port = int(ports[-1])
        if not 1 <= port <= 65535:
            raise RuntimeError("The generated Dockerfile declares an invalid exposed port.")
        return port

    @staticmethod
    def _source_archive(artifacts: dict[str, str]) -> bytes:
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w:gz") as output:
            for path, content in sorted(artifacts.items()):
                normalized = path.replace("\\", "/")
                if (
                    not normalized or normalized.startswith("/") or "\\" in path
                    or any(part in {"", ".", ".."} for part in normalized.split("/"))
                    or (len(normalized) > 1 and normalized[1] == ":")
                    or normalized.split("/", 1)[0].lower() in {".git", ".github"}
                ):
                    raise RuntimeError(f"Refusing to deploy unsafe generated path {path!r}.")
                raw = content.encode("utf-8")
                entry = tarfile.TarInfo(normalized)
                entry.size = len(raw)
                entry.mode = 0o644
                output.addfile(entry, io.BytesIO(raw))
        return archive.getvalue()
