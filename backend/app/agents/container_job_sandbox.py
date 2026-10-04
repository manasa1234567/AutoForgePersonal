from __future__ import annotations

import asyncio
import copy
import json
import os
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx
from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.blob.aio import BlobServiceClient

from ..models.schemas import Blueprint, CriticFinding
from .dynamic_sessions_sandbox import SandboxResult


@dataclass(frozen=True)
class _JobConfig:
    subscription_id: str
    resource_group: str
    job_name: str
    image: str
    container_name: str
    sandbox_client_id: str
    storage_account: str
    storage_container: str
    timeout_seconds: int
    api_version: str


class ContainerAppsJobSandbox:
    """Run one isolated validation per Azure Container Apps Job execution."""

    _max_response_bytes = 1_000_000

    async def validate(
        self,
        *,
        title: str,
        blueprint: Blueprint,
        requirements: list[dict[str, Any]],
        acceptance_criteria: list[str],
        artifacts: dict[str, str],
    ) -> SandboxResult:
        try:
            config = self._config()
            run_id = f"autoforge-{uuid.uuid4().hex}"
            contract = {
                "contractVersion": "1",
                "runId": run_id,
                "title": title[:160],
                "approvedBlueprint": blueprint.model_dump(by_alias=True),
                "approvedRequirements": requirements[:60],
                "acceptanceCriteria": acceptance_criteria[:60],
                "generatedArtifacts": [
                    {"path": path, "content": content}
                    for path, content in artifacts.items()
                ],
                "timeoutSeconds": config.timeout_seconds,
            }
            contract_blob = f"{run_id}/contract.json"
            result_blob = f"{run_id}/result.json"

            credential = self._credential()
            try:
                service = BlobServiceClient(
                    account_url=f"https://{config.storage_account}.blob.core.windows.net",
                    credential=credential,
                )
                try:
                    await self._upload_json(service, config.storage_container, contract_blob, contract)
                    await self._start_job(credential, config, run_id)
                    result_data = await self._wait_for_result(
                        service, config.storage_container, result_blob, config.timeout_seconds + 30
                    )
                finally:
                    await service.close()
            finally:
                await credential.close()

            if result_data is None:
                return self._failure(
                    "Sandbox Job timed out waiting for result.json.",
                    "The Container Apps Job did not return a result before the timeout.",
                    "Inspect the Job execution logs and confirm the runner can read and write the sandbox-runs Blob container.",
                )
            if result_data.get("runId") not in (None, run_id):
                return self._failure(
                    "Sandbox runner returned a result for a different run.",
                    "The result runId did not match the submitted validation.",
                    "Check that the Container Apps Job uses the AutoForge runner image and writes results to the run-specific blob path.",
                )
            result = self._parse_result(result_data)
            return SandboxResult(
                status=result.status,
                summary=result.summary,
                checks={"job_execution": "Passed", **result.checks},
                findings=result.findings,
            )
        except Exception as exc:
            return self._failure(
                "Azure Container Apps Job sandbox execution failed.",
                f"Sandbox infrastructure request failed ({type(exc).__name__}): {str(exc)[:700]}",
                "Check the backend identity's job-start and sandbox Blob permissions, the Job configuration, and the runner identity's Blob access.",
            )

    @staticmethod
    def _required(name: str) -> str:
        value = os.getenv(name, "").strip()
        if not value:
            raise RuntimeError(f"Required environment variable {name} is not set")
        return value

    @classmethod
    def _config(cls) -> _JobConfig:
        timeout_raw = os.getenv("AUTOFORGE_SANDBOX_TIMEOUT_SECONDS", "120")
        try:
            timeout = int(timeout_raw)
        except ValueError as exc:
            raise RuntimeError("AUTOFORGE_SANDBOX_TIMEOUT_SECONDS must be an integer") from exc
        if not 5 <= timeout <= 600:
            raise RuntimeError("AUTOFORGE_SANDBOX_TIMEOUT_SECONDS must be from 5 to 600")

        storage_account = os.getenv("AUTOFORGE_SANDBOX_STORAGE_ACCOUNT", "").strip()
        if not storage_account:
            blob_url = os.getenv("AUTOFORGE_BLOB_ACCOUNT_URL", "").strip()
            if blob_url:
                from urllib.parse import urlsplit

                host = urlsplit(blob_url).hostname or ""
                storage_account = host.split(".", 1)[0]

        return _JobConfig(
            subscription_id=cls._required("AZURE_SUBSCRIPTION_ID"),
            resource_group=os.getenv("AUTOFORGE_SANDBOX_RESOURCE_GROUP", "rg-autoforge").strip(),
            job_name=os.getenv("AUTOFORGE_SANDBOX_JOB_NAME", "af-sandbox-job").strip(),
            image=cls._required("AUTOFORGE_SANDBOX_IMAGE"),
            container_name=os.getenv("AUTOFORGE_SANDBOX_JOB_CONTAINER", "autoforge-runner").strip(),
            sandbox_client_id=cls._required("AUTOFORGE_SANDBOX_CLIENT_ID"),
            storage_account=storage_account or cls._required("AUTOFORGE_SANDBOX_STORAGE_ACCOUNT"),
            storage_container=os.getenv(
                "AUTOFORGE_SANDBOX_CONTAINER",
                os.getenv("AUTOFORGE_SANDBOX_STORAGE_CONTAINER", "sandbox-runs"),
            ).strip(),
            timeout_seconds=timeout,
            api_version=os.getenv("AUTOFORGE_CONTAINER_APPS_API_VERSION", "2025-07-01").strip(),
        )

    @staticmethod
    def _credential():
        if os.getenv("AUTOFORGE_IDENTITY_MODE", "").strip().lower() == "managed_identity":
            client_id = os.getenv("AZURE_CLIENT_ID", "").strip()
            return ManagedIdentityCredential(client_id=client_id) if client_id else ManagedIdentityCredential()
        return DefaultAzureCredential()

    @staticmethod
    async def _upload_json(
        service: BlobServiceClient,
        container_name: str,
        blob_name: str,
        data: dict[str, Any],
    ) -> None:
        blob = service.get_container_client(container_name).get_blob_client(blob_name)
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        await blob.upload_blob(payload, overwrite=True)

    @staticmethod
    async def _download_json(
        service: BlobServiceClient,
        container_name: str,
        blob_name: str,
    ) -> dict[str, Any] | None:
        blob = service.get_container_client(container_name).get_blob_client(blob_name)
        try:
            response = await blob.download_blob()
        except ResourceNotFoundError:
            return None
        content = await response.readall()
        data = json.loads(content.decode("utf-8"))
        if not isinstance(data, dict):
            raise RuntimeError("Sandbox result must be a JSON object")
        return data

    @classmethod
    async def _wait_for_result(
        cls,
        service: BlobServiceClient,
        container_name: str,
        result_blob: str,
        max_wait: int,
    ) -> dict[str, Any] | None:
        elapsed = 0
        while elapsed < max_wait:
            result = await cls._download_json(service, container_name, result_blob)
            if result is not None:
                return result
            delay = min(2, max_wait - elapsed)
            await asyncio.sleep(delay)
            elapsed += delay
        return None

    @staticmethod
    async def _start_job(credential, config: _JobConfig, run_id: str) -> None:
        token = await credential.get_token("https://management.azure.com/.default")
        base = (
            "https://management.azure.com/subscriptions/"
            f"{quote(config.subscription_id, safe='')}/resourceGroups/"
            f"{quote(config.resource_group, safe='')}/providers/Microsoft.App/jobs/"
            f"{quote(config.job_name, safe='')}"
        )
        params = {"api-version": config.api_version}
        headers = {"Authorization": f"Bearer {token.token}", "Content-Type": "application/json"}
        timeout = httpx.Timeout(connect=15, read=60, write=30, pool=15)
        async with httpx.AsyncClient(timeout=timeout) as client:
            job_response = await client.get(base, params=params, headers=headers)
            if job_response.is_error:
                raise RuntimeError(
                    f"Could not read Container Apps Job configuration: HTTP {job_response.status_code} "
                    f"{job_response.text[:1000]}"
                )
            job = job_response.json()
            properties = job.get("properties", {}) if isinstance(job, dict) else {}
            template = properties.get("template", {}) if isinstance(properties, dict) else {}
            containers = template.get("containers", []) if isinstance(template, dict) else []
            if not isinstance(containers, list) or not containers:
                raise RuntimeError("Container Apps Job has no main container in properties.template.containers")

            containers = copy.deepcopy(containers)
            target = next(
                (item for item in containers if isinstance(item, dict) and item.get("name") == config.container_name),
                None,
            )
            if target is None:
                available = ", ".join(
                    str(item.get("name", "")) for item in containers if isinstance(item, dict)
                )
                raise RuntimeError(
                    f"Job container '{config.container_name}' was not found; configured container(s): {available or '(none)'}"
                )

            target["image"] = config.image
            env = target.get("env", [])
            env = [item for item in env if isinstance(item, dict)]
            overrides = {
                "AUTOFORGE_JOB_MODE": "true",
                "AUTOFORGE_RUN_ID": run_id,
                "AZURE_CLIENT_ID": config.sandbox_client_id,
                "AUTOFORGE_SANDBOX_STORAGE_ACCOUNT": config.storage_account,
                "AUTOFORGE_SANDBOX_CONTAINER": config.storage_container,
            }
            names = set(overrides)
            target["env"] = [item for item in env if item.get("name") not in names] + [
                {"name": name, "value": value} for name, value in overrides.items()
            ]

            response = await client.post(
                f"{base}/start",
                params=params,
                headers=headers,
                json={"containers": containers},
            )
            if response.is_error:
                raise RuntimeError(
                    f"Container Apps Job start failed: HTTP {response.status_code} {response.text[:1200]}"
                )

    @classmethod
    def _parse_result(cls, data: dict[str, Any]) -> SandboxResult:
        status = str(data.get("status", "failed")).lower()
        if status not in {"passed", "failed"}:
            status = "failed"
        raw_checks = data.get("checks", [])
        checks: dict[str, str] = {}
        if isinstance(raw_checks, list):
            for item in raw_checks[:100]:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "")).strip()[:120]
                value = str(item.get("status", "failed")).strip().lower()
                if name and value in {"passed", "failed", "skipped"}:
                    detail = str(item.get("detail", "")).strip()[:500]
                    checks[name] = value + (f": {detail}" if detail else "")
        elif isinstance(raw_checks, dict):
            checks = {str(name)[:120]: str(value)[:600] for name, value in list(raw_checks.items())[:100]}
        else:
            raise RuntimeError("Sandbox result checks must be an array or object")
        if not checks:
            raise RuntimeError("Sandbox result must include at least one check")
        if any(value.lower().startswith("failed") for value in checks.values()):
            status = "failed"

        raw_findings = data.get("findings", [])
        if not isinstance(raw_findings, list):
            raise RuntimeError("Sandbox result findings must be an array")
        findings: list[CriticFinding] = []
        for item in raw_findings[:100]:
            if not isinstance(item, dict):
                continue
            severity = str(item.get("severity", "Medium"))
            if severity not in {"Critical", "High", "Medium", "Low"}:
                severity = "Medium"
            findings.append(CriticFinding(
                severity=severity,
                file=str(item["file"])[:500] if item.get("file") else None,
                issue=str(item.get("issue", ""))[:1000],
                recommendation=str(item.get("recommendation", "Review this finding."))[:1000],
            ))
        summary = str(data.get("summary", "Sandbox validation finished."))[:2000]
        return SandboxResult(status=status, summary=summary, checks=checks, findings=findings)

    @staticmethod
    def _failure(summary: str, issue: str, recommendation: str) -> SandboxResult:
        return SandboxResult(
            status="failed",
            summary=summary,
            checks={"job_execution": "Failed", "result_available": "Failed"},
            findings=[CriticFinding(
                severity="High",
                file=None,
                issue=issue[:1000],
                recommendation=recommendation[:1000],
            )],
        )
