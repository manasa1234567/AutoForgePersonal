from __future__ import annotations

import hashlib
import os
from typing import Any

from ..models.schemas import BuildState, DeploymentPlan
from .artifact_limits import MAX_ARTIFACT_FILES, MAX_ARTIFACT_TOTAL_BYTES


class DeployerAgent:
    """Create an evidence-based deployment preflight; do not deploy from local mode."""

    name = "Deployer Agent"
    _required_settings = (
        "AZURE_SUBSCRIPTION_ID",
        "AZURE_RESOURCE_GROUP",
        "ACR_LOGIN_SERVER",
        "ACA_ENVIRONMENT_NAME",
        "ACA_RESOURCE_GROUP",
    )

    async def prepare(self, build: BuildState) -> DeploymentPlan:
        artifacts = build.proof.artifacts if build.proof else {}
        checks: dict[str, str] = {}
        blockers: list[str] = []
        manifest: list[dict[str, Any]] = []

        if not artifacts:
            checks["generated_artifacts"] = "Failed"
            blockers.append("No generated artifacts are available.")
        else:
            invalid_paths = [
                path for path in artifacts
                if not path or path.startswith(("/", "\\")) or "\\" in path
                or any(part in {"", ".", ".."} for part in path.split("/"))
                or (len(path) > 1 and path[1] == ":")
            ]
            total_bytes = sum(len(content.encode("utf-8")) for content in artifacts.values())
            if invalid_paths:
                checks["artifact_paths"] = "Failed"
                blockers.append("Generated file paths must be normalized and project-relative.")
            elif len(artifacts) > MAX_ARTIFACT_FILES or total_bytes > MAX_ARTIFACT_TOTAL_BYTES:
                checks["artifact_bounds"] = "Failed"
                blockers.append(f"Artifacts exceed the configured {MAX_ARTIFACT_FILES}-file or {MAX_ARTIFACT_TOTAL_BYTES // 1000} KB packaging bound.")
            else:
                checks["artifact_paths"] = "Passed"
                checks["artifact_bounds"] = "Passed"
                for path, content in sorted(artifacts.items()):
                    raw = content.encode("utf-8")
                    manifest.append({
                        "path": path,
                        "size_bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(),
                    })

        runtime = build.proof.runtime_status if build.proof else "Not run"
        if runtime.lower().startswith("passed"):
            if "source checks" in runtime.lower() and "not performed" in runtime.lower():
                checks["isolated_source_validation"] = runtime
                checks["image_build_and_startup"] = (
                    "Pending: the release workflow must compile the root Dockerfile and verify HTTP startup before Azure deployment."
                )
            else:
                checks["isolated_runtime_validation"] = runtime
        else:
            checks["isolated_runtime_validation"] = runtime
            blockers.append("Isolated build and test validation has not passed.")

        review = build.security_review
        if review is None:
            checks["security_review"] = "Not run"
            blockers.append("Security Reviewer has not reviewed the generated artifacts.")
        else:
            high_findings = [item for item in review.findings if item.severity in {"Critical", "High"}]
            checks["security_review"] = f"{review.decision}; {len(high_findings)} high/critical finding(s)"
            if review.decision == "Block release" or high_findings:
                blockers.append("Resolve all high and critical Security Reviewer findings.")
            for name, state in review.external_scans.items():
                checks[name] = state
                if state.lower().startswith("not run") or state.lower().startswith("failed"):
                    blockers.append(f"Required security evidence is missing: {name}.")

        missing_settings = [key for key in self._required_settings if not os.getenv(key, "").strip()]
        for key in self._required_settings:
            checks[f"config:{key}"] = "Configured" if key not in missing_settings else "Missing"
        if missing_settings:
            blockers.append("Azure deployment configuration is incomplete: " + ", ".join(missing_settings) + ".")
        identity_mode = os.getenv("AUTOFORGE_IDENTITY_MODE", "").lower()
        checks["managed_identity"] = "Configured" if identity_mode == "managed_identity" else "Not configured"
        if identity_mode != "managed_identity":
            blockers.append("Azure deployment must use the provisioned managed identity.")

        deploy_enabled = os.getenv("AUTOFORGE_DEPLOYMENT_ENABLED", "false").lower() == "true"
        checks["deployment_enabled"] = "Enabled" if deploy_enabled else "Disabled"
        if not deploy_enabled:
            blockers.append("Deployment remains disabled by AUTOFORGE_DEPLOYMENT_ENABLED.")
        else:
            checks["deployment_adapter"] = "GitHub Actions generated-app workflow configured"

        target = build.blueprint.deployment if build.blueprint else "Not specified in approved blueprint"
        unique_blockers = list(dict.fromkeys(blockers))
        status = "blocked" if unique_blockers else "ready"
        summary = (
            "Deployment preflight is ready for the human approval gate. No deployment was started."
            if status == "ready" else
            f"Deployment preflight found {len(unique_blockers)} blocker(s). No deployment was started."
        )
        return DeploymentPlan(
            status=status,
            summary=summary,
            target=target,
            image_tag=f"autoforge/{build.id}:candidate",
            human_approval_required=True,
            checks=checks,
            blockers=unique_blockers,
            artifact_manifest=manifest,
        )
