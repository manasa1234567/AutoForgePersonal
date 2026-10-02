from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx


ISSUE_KEY = re.compile(r"^[A-Z][A-Z0-9]+-\d+$", re.IGNORECASE)
CUSTOM_FIELD_ID = re.compile(r"^customfield_\d+$")


@dataclass(frozen=True)
class JiraIssue:
    key: str
    summary: str
    description: str
    issue_type: str
    acceptance_criteria: str = ""


class JiraClient:
    """Read-only Jira Cloud issue resolver for the AutoForge intake flow."""

    @staticmethod
    def configured() -> bool:
        return all(
            os.getenv(name, "").strip()
            for name in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")
        )

    async def get_issue(self, key: str) -> JiraIssue:
        key = key.strip()
        if not ISSUE_KEY.fullmatch(key):
            raise ValueError("Enter a Jira issue key such as PAY-142")

        base_url = os.getenv("JIRA_BASE_URL", "").strip().rstrip("/")
        email = os.getenv("JIRA_EMAIL", "").strip()
        token = os.getenv("JIRA_API_TOKEN", "").strip()
        if not base_url or not email or not token:
            raise RuntimeError(
                "Jira integration is not configured. Set JIRA_BASE_URL, JIRA_EMAIL, "
                "and JIRA_API_TOKEN on the backend."
            )

        parsed = urlparse(base_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise RuntimeError("JIRA_BASE_URL must be an HTTPS Jira Cloud site URL without embedded credentials")

        criteria_field = os.getenv("JIRA_ACCEPTANCE_CRITERIA_FIELD", "").strip()
        if criteria_field and not CUSTOM_FIELD_ID.fullmatch(criteria_field):
            raise RuntimeError("JIRA_ACCEPTANCE_CRITERIA_FIELD must use the customfield_NNNNN format")
        fields = ["summary", "description", "issuetype"]
        if criteria_field:
            fields.append(criteria_field)

        url = f"{base_url}/rest/api/3/issue/{key}"
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
                response = await client.get(
                    url,
                    params={"fields": ",".join(fields)},
                    headers={"Accept": "application/json"},
                    auth=(email, token),
                )
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Could not reach Jira ({type(exc).__name__})") from exc

        if response.status_code == 401:
            raise RuntimeError("Jira rejected the configured account or API token")
        if response.status_code == 403:
            raise RuntimeError("The configured Jira account cannot browse this project or issue")
        if response.status_code == 404:
            raise RuntimeError(f"Jira issue {key.upper()} was not found or is not visible to this account")
        if response.is_error:
            raise RuntimeError(f"Jira issue lookup failed (HTTP {response.status_code})")

        try:
            payload = response.json()
            issue_fields = payload["fields"]
            summary = str(issue_fields.get("summary", "")).strip()
            if not summary:
                raise ValueError("missing issue summary")
            description = self._plain_text(issue_fields.get("description"))
            issue_type = str((issue_fields.get("issuetype") or {}).get("name", ""))
            acceptance_criteria = self._plain_text(issue_fields.get(criteria_field)) if criteria_field else ""
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("Jira returned an issue without a usable summary") from exc

        return JiraIssue(
            key=str(payload.get("key", key)).upper(),
            summary=summary,
            description=description,
            issue_type=issue_type,
            acceptance_criteria=acceptance_criteria,
        )

    @classmethod
    def _plain_text(cls, value: object) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            return " ".join(part for item in value if (part := cls._plain_text(item)))
        if isinstance(value, dict):
            if isinstance(value.get("text"), str):
                return value["text"].strip()
            content = value.get("content")
            if isinstance(content, list):
                parts = [part for item in content if (part := cls._plain_text(item))]
                separator = "\n" if value.get("type") in {"paragraph", "heading", "listItem"} else " "
                return separator.join(parts)
        return ""
