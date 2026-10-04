from __future__ import annotations

import asyncio
import json
import os
import uuid
from typing import Any

import httpx
from azure.identity.aio import (
    DefaultAzureCredential,
    ManagedIdentityCredential,
)
from azure.storage.blob.aio import BlobServiceClient

from ..models.schemas import (
    Blueprint,
    CriticFinding,
)
from .dynamic_sessions_sandbox import SandboxResult


class ContainerAppsJobSandbox:
    """
    Executes generated artifacts through an Azure Container Apps Job.

    Flow:

        Backend
           |
           | contract.json
           v
        Azure Blob Storage
           |
           | start Job + AUTOFORGE_RUN_ID
           v
        Container Apps Job
           |
           v
        sandbox-runner
           |
           | result.json
           v
        Azure Blob Storage
           |
           v
        Backend
    """

    def __init__(self) -> None:
        self.subscription_id = self._required(
            "AZURE_SUBSCRIPTION_ID"
        )

        self.resource_group = os.getenv(
            "AUTOFORGE_SANDBOX_RESOURCE_GROUP",
            "rg-autoforge",
        )

        self.job_name = os.getenv(
            "AUTOFORGE_SANDBOX_JOB_NAME",
            "af-sandbox-job",
        )

        self.storage_account = os.getenv(
            "AUTOFORGE_SANDBOX_STORAGE_ACCOUNT",
            "afstorage5usl4p",
        )

        self.storage_container = os.getenv(
            "AUTOFORGE_SANDBOX_STORAGE_CONTAINER",
            "sandbox-runs",
        )

        self.timeout_seconds = self._timeout_seconds()

        # Azure Container Apps Jobs Start API.
        self.management_api_version = os.getenv(
            "AUTOFORGE_CONTAINER_APPS_API_VERSION",
            "2025-07-01",
        )

    # =============================================================
    # PUBLIC
    # =============================================================

    async def validate(
        self,
        *,
        title: str,
        blueprint: Blueprint,
        requirements: list[dict[str, Any]],
        acceptance_criteria: list[str],
        artifacts: dict[str, str],
    ) -> SandboxResult:

        # Every sandbox run gets a unique ID.
        run_id = f"autoforge-{uuid.uuid4().hex}"

        contract = {
            "contractVersion": "1",
            "runId": run_id,
            "title": title[:160],
            "approvedBlueprint": blueprint.model_dump(
                by_alias=True
            ),
            "approvedRequirements": requirements[:60],
            "acceptanceCriteria": acceptance_criteria[:60],
            "generatedArtifacts": [
                {
                    "path": path,
                    "content": content,
                }
                for path, content in artifacts.items()
            ],
            "timeoutSeconds": self.timeout_seconds,
        }

        contract_blob = f"{run_id}/contract.json"
        result_blob = f"{run_id}/result.json"

        try:
            # -----------------------------------------------------
            # 1. Upload contract
            # -----------------------------------------------------

            await self._upload_json(
                blob_name=contract_blob,
                data=contract,
            )

            # -----------------------------------------------------
            # 2. Start Container Apps Job
            #
            # IMPORTANT:
            # AUTOFORGE_RUN_ID is passed dynamically for this
            # specific execution.
            # -----------------------------------------------------

            await self._start_job(run_id)

            # -----------------------------------------------------
            # 3. Wait for runner result
            # -----------------------------------------------------

            result = await self._wait_for_result(
                result_blob
            )

            if result is None:
                return SandboxResult(
                    status="failed",
                    summary=(
                        "Sandbox Job timed out waiting "
                        "for result.json"
                    ),
                    checks={
                        "job_execution": "Failed",
                        "result_available": "Failed",
                    },
                    findings=[
                        CriticFinding(
                            severity="Critical",
                            file=None,
                            issue=(
                                "The Azure Container Apps sandbox "
                                "Job did not produce a result "
                                "within the configured timeout."
                            ),
                            recommendation=(
                                "Inspect the Container Apps Job "
                                "execution logs and runner container."
                            ),
                        )
                    ],
                )

            # -----------------------------------------------------
            # 4. Parse result
            # -----------------------------------------------------

            return self._parse_result(result)

        except Exception as exc:
            return SandboxResult(
                status="failed",
                summary=(
                    "Azure Container Apps Job sandbox "
                    "execution failed."
                ),
                checks={
                    "job_execution": "Failed",
                    "result_available": "Failed",
                },
                findings=[
                    CriticFinding(
                        severity="Critical",
                        file=None,
                        issue=(
                            "Sandbox infrastructure request failed: "
                            f"{type(exc).__name__}: {str(exc)[:1000]}"
                        ),
                        recommendation=(
                            "Inspect Azure Container Apps Job, "
                            "Managed Identity, Blob Storage permissions, "
                            "and runner logs."
                        ),
                    )
                ],
            )

    # =============================================================
    # CONFIG
    # =============================================================

    @staticmethod
    def _required(name: str) -> str:
        value = os.getenv(name, "").strip()

        if not value:
            raise RuntimeError(
                f"Required environment variable {name} is not set."
            )

        return value

    def _timeout_seconds(self) -> int:
        raw = os.getenv(
            "AUTOFORGE_SANDBOX_TIMEOUT_SECONDS",
            "120",
        )

        try:
            value = int(raw)
        except ValueError as exc:
            raise RuntimeError(
                "AUTOFORGE_SANDBOX_TIMEOUT_SECONDS "
                "must be an integer."
            ) from exc

        return max(
            5,
            min(value, 600),
        )

    # =============================================================
    # IDENTITY
    # =============================================================

    def _credential(self):
        identity_mode = os.getenv(
            "AUTOFORGE_IDENTITY_MODE",
            "managed_identity",
        ).lower()

        if identity_mode == "managed_identity":
            client_id = os.getenv(
                "AZURE_CLIENT_ID"
            )

            if client_id:
                return ManagedIdentityCredential(
                    client_id=client_id
                )

            return ManagedIdentityCredential()

        return DefaultAzureCredential()

    # =============================================================
    # BLOB STORAGE
    # =============================================================

    def _blob_service_url(self) -> str:
        return (
            f"https://{self.storage_account}"
            ".blob.core.windows.net"
        )

    async def _upload_json(
        self,
        *,
        blob_name: str,
        data: dict[str, Any],
    ) -> None:

        credential = self._credential()

        try:
            service = BlobServiceClient(
                account_url=self._blob_service_url(),
                credential=credential,
            )

            try:
                container = service.get_container_client(
                    self.storage_container
                )

                blob = container.get_blob_client(
                    blob_name
                )

                payload = json.dumps(
                    data,
                    ensure_ascii=False,
                ).encode("utf-8")

                await blob.upload_blob(
                    payload,
                    overwrite=True,
                )

            finally:
                await service.close()

        finally:
            await credential.close()

    async def _download_json(
        self,
        blob_name: str,
    ) -> dict[str, Any] | None:

        credential = self._credential()

        try:
            service = BlobServiceClient(
                account_url=self._blob_service_url(),
                credential=credential,
            )

            try:
                container = service.get_container_client(
                    self.storage_container
                )

                blob = container.get_blob_client(
                    blob_name
                )

                try:
                    response = await blob.download_blob()
                    content = await response.readall()

                except Exception:
                    return None

                data = json.loads(
                    content.decode("utf-8")
                )

                if not isinstance(data, dict):
                    return None

                return data

            finally:
                await service.close()

        finally:
            await credential.close()

    # =============================================================
    # START JOB
    # =============================================================

    async def _start_job(
        self,
        run_id: str,
    ) -> None:

        credential = self._credential()

        try:
            # -----------------------------------------------------
            # Get Azure Resource Manager token
            # -----------------------------------------------------

            token = await credential.get_token(
                "https://management.azure.com/.default"
            )

            # -----------------------------------------------------
            # Azure Container Apps Job Start endpoint
            # -----------------------------------------------------

            url = (
                "https://management.azure.com"
                f"/subscriptions/{self.subscription_id}"
                f"/resourceGroups/{self.resource_group}"
                f"/providers/Microsoft.App/jobs/{self.job_name}"
                f"/start?api-version={self.management_api_version}"
            )

            # -----------------------------------------------------
            # IMPORTANT
            #
            # The Start API expects containers directly.
            #
            # We dynamically inject AUTOFORGE_RUN_ID for this
            # execution.
            # -----------------------------------------------------

            payload = {
                "containers": [
                    {
                        "name": "autoforge-runner",
                        "env": [
                            {
                                "name": "AUTOFORGE_JOB_MODE",
                                "value": "true",
                            },
                            {
                                "name": "AUTOFORGE_RUN_ID",
                                "value": run_id,
                            },
                        ],
                    }
                ]
            }

            headers = {
                "Authorization": (
                    f"Bearer {token.token}"
                ),
                "Content-Type": "application/json",
            }

            timeout = httpx.Timeout(
                connect=15,
                read=60,
                write=30,
                pool=15,
            )

            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:

                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )

                if response.status_code >= 400:
                    raise RuntimeError(
                        "Azure Container Apps Job start failed: "
                        f"HTTP {response.status_code} "
                        f"{response.text[:2000]}"
                    )

        finally:
            await credential.close()

    # =============================================================
    # WAIT FOR RESULT
    # =============================================================

    async def _wait_for_result(
        self,
        result_blob: str,
    ) -> dict[str, Any] | None:

        # Give the Job a little room beyond the configured runner
        # timeout to upload its result.
        max_wait = self.timeout_seconds + 30

        interval = 2
        elapsed = 0

        while elapsed < max_wait:

            result = await self._download_json(
                result_blob
            )

            if result is not None:
                return result

            await asyncio.sleep(interval)

            elapsed += interval

        return None

    # =============================================================
    # RESULT PARSING
    # =============================================================

    @staticmethod
    def _parse_result(
        data: dict[str, Any],
    ) -> SandboxResult:

        status = str(
            data.get(
                "status",
                "failed",
            )
        ).lower()

        if status not in {
            "passed",
            "failed",
        }:
            status = "failed"

        summary = str(
            data.get(
                "summary",
                "Sandbox runner returned no summary.",
            )
        )[:2000]

        raw_checks = data.get(
            "checks",
            [],
        )

        checks: dict[str, str] = {}

        if isinstance(raw_checks, list):

            for item in raw_checks:

                if not isinstance(item, dict):
                    continue

                name = str(
                    item.get(
                        "name",
                        "",
                    )
                ).strip()

                check_status = str(
                    item.get(
                        "status",
                        "failed",
                    )
                ).strip()

                if name:
                    checks[name] = check_status

        elif isinstance(raw_checks, dict):

            for name, value in raw_checks.items():
                checks[str(name)] = str(value)

        raw_findings = data.get(
            "findings",
            [],
        )

        findings: list[CriticFinding] = []

        if isinstance(raw_findings, list):

            for item in raw_findings:

                if not isinstance(item, dict):
                    continue

                severity = str(
                    item.get(
                        "severity",
                        "Medium",
                    )
                )

                if severity not in {
                    "Critical",
                    "High",
                    "Medium",
                    "Low",
                }:
                    severity = "Medium"

                findings.append(
                    CriticFinding(
                        severity=severity,
                        file=(
                            str(item["file"])
                            if item.get("file")
                            else None
                        ),
                        issue=str(
                            item.get(
                                "issue",
                                "",
                            )
                        )[:1000],
                        recommendation=str(
                            item.get(
                                "recommendation",
                                "Review the finding.",
                            )
                        )[:1000],
                    )
                )

        return SandboxResult(
            status=status,
            summary=summary,
            checks=checks,
            findings=findings[:100],
        )