from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urlsplit

import httpx

from ..models.schemas import Blueprint, CriticFinding


@dataclass(frozen=True)
class SandboxResult:
    status: str
    summary: str
    checks: dict[str, str]
    findings: list[CriticFinding]


class DynamicSessionsSandbox:
    """Client for the AutoForge validation endpoint hosted in a custom ACA session pool."""

    _route_pattern = re.compile(r"^/[A-Za-z0-9/_-]{1,100}$")
    _identifier_prefix = "autoforge-"
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
        endpoint = os.getenv("AUTOFORGE_SANDBOX_ENDPOINT", "").strip().rstrip("/")
        if not endpoint:
            raise RuntimeError("AUTOFORGE_SANDBOX_ENDPOINT is required when the sandbox is enabled")
        parsed = urlsplit(endpoint)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise RuntimeError("AUTOFORGE_SANDBOX_ENDPOINT must be an HTTPS pool management endpoint")

        route = os.getenv("AUTOFORGE_SANDBOX_ROUTE", "/autoforge/validate").strip()
        if not self._route_pattern.fullmatch(route) or "//" in route or ".." in route:
            raise RuntimeError("AUTOFORGE_SANDBOX_ROUTE must be a relative path such as /autoforge/validate")

        timeout_seconds = self._timeout_seconds()
        try:
            from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential
        except ImportError as exc:
            raise RuntimeError("Install azure-identity to call the Azure Container Apps session pool") from exc

        if os.getenv("AUTOFORGE_IDENTITY_MODE", "").lower() == "managed_identity":
            client_id = os.getenv("AZURE_CLIENT_ID")
            credential = ManagedIdentityCredential(client_id=client_id) if client_id else ManagedIdentityCredential()
        else:
            credential = DefaultAzureCredential()

        identifier = f"{self._identifier_prefix}{uuid.uuid4().hex}"
        payload = {
            "contractVersion": "1",
            "title": title[:160],
            "approvedBlueprint": blueprint.model_dump(by_alias=True),
            "approvedRequirements": requirements[:60],
            "acceptanceCriteria": acceptance_criteria[:60],
            "artifacts": artifacts,
            "timeoutSeconds": timeout_seconds,
        }
        try:
            token = await credential.get_token("https://dynamicsessions.io/.default")
            async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=False) as client:
                async with client.stream(
                    "POST",
                    f"{endpoint}{route}?{urlencode({'identifier': identifier})}",
                    headers={"Authorization": f"Bearer {token.token}", "Content-Type": "application/json"},
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > self._max_response_bytes:
                            raise RuntimeError("Sandbox response exceeded the 1 MB response limit")
            try:
                data = json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise RuntimeError("Sandbox runner returned invalid JSON") from exc
            return self._parse_result(data)
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"Sandbox validation exceeded its {timeout_seconds}s request timeout") from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"Sandbox runner returned HTTP {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Sandbox runner request failed ({type(exc).__name__})") from exc
        finally:
            await credential.close()

    @staticmethod
    def _timeout_seconds() -> int:
        raw = os.getenv("AUTOFORGE_SANDBOX_TIMEOUT_SECONDS", "120")
        try:
            value = int(raw)
        except ValueError as exc:
            raise RuntimeError("AUTOFORGE_SANDBOX_TIMEOUT_SECONDS must be an integer from 5 to 600") from exc
        if value < 5 or value > 600:
            raise RuntimeError("AUTOFORGE_SANDBOX_TIMEOUT_SECONDS must be an integer from 5 to 600")
        return value

    @staticmethod
    def _parse_result(data: Any) -> SandboxResult:
        if not isinstance(data, dict) or data.get("contractVersion") != "1":
            raise RuntimeError("Sandbox runner response does not match contract version 1")
        status = data.get("status")
        if status not in {"passed", "failed"}:
            raise RuntimeError("Sandbox runner must return status 'passed' or 'failed'")
        checks_data = data.get("checks")
        if not isinstance(checks_data, list) or not checks_data:
            raise RuntimeError("Sandbox runner must return at least one named check")
        checks: dict[str, str] = {}
        for item in checks_data[:100]:
            if not isinstance(item, dict) or item.get("status") not in {"passed", "failed", "skipped"}:
                raise RuntimeError("Sandbox runner returned a malformed check")
            name = str(item.get("name", "")).strip()[:120]
            if not name:
                raise RuntimeError("Sandbox runner returned a check without a name")
            checks[name] = item["status"] + (f": {str(item.get('detail', '')).strip()[:500]}" if item.get("detail") else "")
        if any(value.startswith("failed") for value in checks.values()):
            status = "failed"
        if status == "passed" and not any(value.startswith("passed") for value in checks.values()):
            raise RuntimeError("Sandbox runner cannot pass a run without reporting a passed check")

        findings_data = data.get("findings", [])
        if not isinstance(findings_data, list):
            raise RuntimeError("Sandbox runner findings must be an array")
        findings: list[CriticFinding] = []
        for item in findings_data[:100]:
            if not isinstance(item, dict):
                raise RuntimeError("Sandbox runner returned a malformed finding")
            try:
                finding = CriticFinding.model_validate(item)
            except Exception as exc:
                raise RuntimeError("Sandbox runner returned an invalid finding") from exc
            findings.append(finding)
        for name, value in checks.items():
            if value.startswith("failed") and not any(name in finding.issue for finding in findings):
                detail = value.partition(": ")[2] or "The sandbox check failed."
                findings.append(CriticFinding(
                    severity="High",
                    file=None,
                    issue=f"Sandbox check '{name}' failed: {detail}"[:1000],
                    recommendation="Correct the reported build or test failure, then rerun the isolated validation.",
                ))
        if any(item.severity == "Critical" for item in findings):
            status = "failed"

        return SandboxResult(
            status=status,
            summary=str(data.get("summary", "Sandbox validation finished."))[:2000],
            checks=checks,
            findings=findings,
        )
