from __future__ import annotations

import os

from fastapi import APIRouter

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


def _configured(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


@router.get("/deployment-status")
async def deployment_status() -> dict[str, object]:
    """Expose deployment readiness without returning credential values."""
    github = {
        "repository": _configured("AUTOFORGE_GITHUB_OWNER") and _configured("AUTOFORGE_GITHUB_REPOSITORY"),
        "app_identity": all(_configured(name) for name in (
            "AUTOFORGE_GITHUB_APP_ID", "AUTOFORGE_GITHUB_INSTALLATION_ID", "AUTOFORGE_GITHUB_APP_PRIVATE_KEY_BASE64",
        )),
        "branch_publishing_enabled": os.getenv("AUTOFORGE_GITHUB_PUBLISH_ENABLED", "false").lower() == "true",
        "contents_permission": "Requires the installed GitHub App to have Contents read/write access. Pull request access is not used.",
    }
    azure = {
        "subscription": _configured("AZURE_SUBSCRIPTION_ID"),
        "resource_group": _configured("AZURE_RESOURCE_GROUP"),
        "container_registry": _configured("ACR_LOGIN_SERVER"),
        "container_apps_environment": _configured("ACA_ENVIRONMENT_NAME") and _configured("ACA_RESOURCE_GROUP"),
        "managed_identity": os.getenv("AUTOFORGE_IDENTITY_MODE", "").lower() == "managed_identity",
        "deployment_enabled": os.getenv("AUTOFORGE_DEPLOYMENT_ENABLED", "false").lower() == "true",
    }
    runtime = {
        "isolated_validation": os.getenv("AUTOFORGE_SANDBOX_ENABLED", "false").lower() == "true"
        and _configured("AUTOFORGE_SANDBOX_ENDPOINT"),
    }
    configured = all(value is True for value in github.values() if isinstance(value, bool)) \
        and all(value is True for value in azure.values()) \
        and all(value is True for value in runtime.values())
    return {
        "status": "configured" if configured else "setup_required",
        "github": github,
        "azureContainerApps": azure,
        "validation": runtime,
        "branchPattern": "feature/<use-case-slug>-<build-id>",
        "branchPublishingImplemented": True,
        "deploymentImplemented": False,
        "note": "After release approval, reviewed artifacts can be committed to a new feature branch. Azure app packaging/deployment and returning a live URL are still pending.",
    }
