from __future__ import annotations

import re
from typing import Any

from ..models.schemas import CriticFinding, SecurityReview, SkillRecipe, SkillUsage


class SecurityReviewer:
    """Evidence-based local source review; never executes generated artifacts."""

    name = "Security Reviewer"
    _secret_patterns = (
        re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret|password|access[_-]?token|secret)\s*[:=]\s*['\"](?!your_|<|\$\{)[^'\"\s]{8,}['\"]"),
        re.compile(r"(?i)AccountKey=[^;\s]{20,}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    )
    _danger_patterns = (
        (re.compile(r"\beval\s*\("), "Dynamic eval can execute attacker-controlled input.", "Remove eval and use explicit parsing or dispatch."),
        (re.compile(r"\bexec\s*\("), "Dynamic exec can execute attacker-controlled input.", "Remove exec and use explicit function calls."),
        (re.compile(r"\bos\.system\s*\("), "os.system invokes a shell with a command string.", "Use a fixed executable and argument list, with validated inputs."),
        (re.compile(r"shell\s*=\s*True", re.I), "A subprocess call enables shell interpretation.", "Pass an argument array and keep shell execution disabled."),
        (re.compile(r"\bpickle\.loads?\s*\("), "Untrusted pickle data can execute code during deserialization.", "Use a data-only serialization format such as JSON."),
        (re.compile(r"yaml\.load\s*\((?![^)]*SafeLoader)", re.S), "yaml.load may construct unsafe Python objects.", "Use yaml.safe_load for untrusted YAML."),
    )
    _config_patterns = (
        (re.compile(r"(?i)verify\s*=\s*False|CERT_NONE"), "TLS certificate verification appears disabled.", "Enable certificate verification and use a trusted CA."),
        (re.compile(r"(?i)allow_origins\s*=\s*\[\s*['\"]\*['\"]"), "CORS allows every origin.", "Restrict CORS to approved application origins."),
        (re.compile(r"(?i)(?:debug\s*[:=]\s*true|DEBUG\s*=\s*true)"), "Debug mode appears enabled in configuration.", "Disable debug mode in release configuration."),
        (re.compile(r"(?i)md5\s*\(|sha1\s*\("), "A weak hash function is used.", "Use a modern cryptographic hash for integrity, or a password hashing scheme for credentials."),
    )

    async def review(
        self,
        *,
        artifacts: dict[str, str],
        skills: list[SkillRecipe] | None = None,
        requirements: list[dict[str, Any]] | None = None,
        security_controls: list[str] | None = None,
        blueprint_choices: dict[str, str] | None = None,
    ) -> SecurityReview:
        findings: list[CriticFinding] = []
        checks = {
            "artifact_paths": "Passed",
            "embedded_secrets": "Passed",
            "dangerous_code_patterns": "Passed",
            "security_configuration": "Passed",
            "dependency_manifest": "Not present",
        }
        if not artifacts:
            checks["artifact_paths"] = "Failed"
            findings.append(CriticFinding(
                severity="Critical", issue="No generated artifacts were provided for security review.",
                recommendation="Generate source artifacts before requesting the Security Reviewer."))

        for path, content in artifacts.items():
            if (not path or path.startswith(("/", "\\")) or "\\" in path or
                    any(part in {"", ".", ".."} for part in path.split("/")) or
                    (len(path) > 1 and path[1] == ":")):
                checks["artifact_paths"] = "Failed"
                findings.append(CriticFinding(
                    severity="Critical", file=path[:500], issue="Artifact path escapes or is not normalized within the project.",
                    recommendation="Use normalized project-relative paths."))

            for pattern in self._secret_patterns:
                if pattern.search(content):
                    checks["embedded_secrets"] = "Failed"
                    findings.append(CriticFinding(
                        severity="Critical", file=path, issue="A credential or private key pattern is embedded in source.",
                        recommendation="Remove the secret, rotate it if real, and load credentials from managed identity or a secret store."))
                    break

            for pattern, issue, recommendation in self._danger_patterns:
                if pattern.search(content):
                    checks["dangerous_code_patterns"] = "Failed"
                    findings.append(CriticFinding(
                        severity="High", file=path, issue=issue, recommendation=recommendation))

            for pattern, issue, recommendation in self._config_patterns:
                if pattern.search(content):
                    checks["security_configuration"] = "Failed"
                    findings.append(CriticFinding(
                        severity="High", file=path, issue=issue, recommendation=recommendation))

            if path.rsplit("/", 1)[-1].lower() in {
                "requirements.txt", "pyproject.toml", "poetry.lock", "package.json",
                "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "pom.xml", "go.mod",
            }:
                checks["dependency_manifest"] = "Present; CVE scan not run"

        blueprint_choices = blueprint_choices or {}
        deployment = blueprint_choices.get("deployment", "")
        identity = blueprint_choices.get("identity", "")
        public_ingress = bool(re.search(r"(?i)public|internet[- ]facing|external ingress", deployment))
        unauthenticated = bool(re.search(r"(?i)\b(no auth|no authentication|anonymous|unauthenticated|none)\b", identity))
        if public_ingress:
            severity = "High" if unauthenticated else "Medium"
            findings.append(CriticFinding(
                severity=severity,
                file=None,
                issue="The approved blueprint describes public ingress" + (" with no authentication" if unauthenticated else ""),
                recommendation="Confirm the ingress boundary and require approved authentication and authorization before release.",
            ))

        findings = self._deduplicate(findings)
        blocking = any(item.severity in {"Critical", "High"} for item in findings)
        skill_usage = [SkillUsage(id=item.id, version=item.version, usage="retrieved") for item in (skills or [])]
        external_scans = {
            "dependency_vulnerabilities": "Not run locally; no offline vulnerability database/scanner configured",
            "container_image": "Not run; no release image was built",
            "runtime_and_cloud_policy": "Not run; Azure services are not connected",
        }
        count = len(artifacts)
        summary = (
            f"Local static review inspected {count} generated file(s), found {len(findings)} issue(s), "
            "and did not execute generated code. Dependency CVEs, image vulnerabilities, and Azure policy were not scanned."
        )
        if security_controls:
            summary += f" {len(security_controls)} approved blueprint security control(s) were included as review context."
        if requirements:
            summary += f" {len(requirements)} approved requirement(s) were included as review context."
        return SecurityReview(
            mode="local-static-security-review",
            decision="Block release" if blocking else "No high or critical findings",
            summary=summary,
            checks=checks,
            findings=findings,
            scanned_files=count,
            skills_used=skill_usage,
            external_scans=external_scans,
        )

    @staticmethod
    def _deduplicate(findings: list[CriticFinding]) -> list[CriticFinding]:
        unique: dict[tuple[str, str | None, str], CriticFinding] = {}
        for item in findings:
            unique[(item.severity, item.file, item.issue)] = item
        return list(unique.values())[:100]
