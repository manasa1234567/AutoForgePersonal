from __future__ import annotations

import ast
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from azure.identity import (
    DefaultAzureCredential,
    ManagedIdentityCredential,
)
from azure.storage.blob import BlobServiceClient


# ================================================================
# FASTAPI APPLICATION
# ================================================================

app = FastAPI(
    title="AutoForge Sandbox Runner"
)


# ================================================================
# CONSTANTS
# ================================================================

MAX_FILES = 128

MAX_FILE_BYTES = 30_000

MAX_TOTAL_BYTES = 100_000

MAX_RESULT_BYTES = 1_000_000


SECRET_PATTERNS = (
    re.compile(
        r"""(?i)(?:api[_-]?key|client[_-]?secret|account[_-]?key|password|secret|access[_-]?token)\s*[:=]\s*['"][^'"]{8,}['"]"""
    ),
    re.compile(
        r"(?i)AccountKey=[^;\s]{20,}"
    ),
    re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    re.compile(
        r"\bAKIA[0-9A-Z]{16}\b"
    ),
    re.compile(
        r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"
    ),
)


# ================================================================
# PYDANTIC MODELS
# ================================================================

class Artifact(BaseModel):
    path: str
    content: str


class ValidationRequest(BaseModel):
    contractVersion: str

    title: str

    approvedBlueprint: dict[str, Any] = Field(
        default_factory=dict
    )

    approvedRequirements: list[Any] = Field(
        default_factory=list
    )

    acceptanceCriteria: list[Any] = Field(
        default_factory=list
    )

    generatedArtifacts: list[Artifact]

    timeoutSeconds: int = Field(
        default=120,
        ge=5,
        le=600,
    )


class Check(BaseModel):
    name: str
    status: str
    detail: str


# ================================================================
# HEALTH
# ================================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/ready")
def ready():
    return {
        "status": "ready"
    }


# ================================================================
# HTTP VALIDATION ENDPOINT
#
# Used by Dynamic Sessions.
# ================================================================

@app.post("/autoforge/validate")
def validate(
    request: ValidationRequest,
):

    if request.contractVersion != "1":

        raise HTTPException(
            status_code=400,
            detail="Unsupported contract version",
        )

    return validate_contract(
        contract=request.model_dump()
    )


# ================================================================
# CORE VALIDATOR
# ================================================================

def validate_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:

    if contract.get("contractVersion") != "1":

        return {
            "contractVersion": "1",
            "status": "failed",
            "summary": "Unsupported contract version",
            "checks": [],
            "findings": [
                {
                    "severity": "Critical",
                    "file": None,
                    "issue": (
                        "The supplied contract version "
                        "is not supported."
                    ),
                    "recommendation": (
                        "Use contractVersion '1'."
                    ),
                }
            ],
        }

    artifacts = contract.get(
        "generatedArtifacts",
        [],
    )

    if not isinstance(
        artifacts,
        list,
    ):

        return {
            "contractVersion": "1",
            "status": "failed",
            "summary": (
                "generatedArtifacts must be an array"
            ),
            "checks": [],
            "findings": [
                {
                    "severity": "Critical",
                    "file": None,
                    "issue": (
                        "The generatedArtifacts field "
                        "is not an array."
                    ),
                    "recommendation": (
                        "Provide generatedArtifacts as "
                        "an array of path/content objects."
                    ),
                }
            ],
        }

    # ------------------------------------------------------------
    # FILE COUNT
    # ------------------------------------------------------------

    if len(artifacts) > MAX_FILES:

        return {
            "contractVersion": "1",
            "status": "failed",
            "summary": (
                "Artifact count limit exceeded"
            ),
            "checks": [
                {
                    "name": "artifact-count",
                    "status": "failed",
                    "detail": (
                        f"Maximum {MAX_FILES} files allowed."
                    ),
                }
            ],
            "findings": [
                {
                    "severity": "Critical",
                    "file": None,
                    "issue": (
                        f"Generated artifact count exceeds "
                        f"{MAX_FILES} files."
                    ),
                    "recommendation": (
                        "Reduce the generated project "
                        "before runtime validation."
                    ),
                }
            ],
        }

    # ------------------------------------------------------------
    # WORKSPACE
    # ------------------------------------------------------------

    workspace = Path(
        tempfile.mkdtemp(
            prefix="autoforge-"
        )
    )

    try:

        findings: list[dict[str, Any]] = []

        checks: list[dict[str, Any]] = []

        total_bytes = 0

        materialized_files: list[tuple[str, Path]] = []

        # --------------------------------------------------------
        # MATERIALIZE ARTIFACTS
        # --------------------------------------------------------

        for artifact in artifacts:

            if not isinstance(
                artifact,
                dict,
            ):
                findings.append(
                    {
                        "severity": "Critical",
                        "file": None,
                        "issue": (
                            "Invalid artifact object."
                        ),
                        "recommendation": (
                            "Each artifact must contain "
                            "path and content."
                        ),
                    }
                )
                continue

            path_string = str(
                artifact.get(
                    "path",
                    "",
                )
            )

            content = str(
                artifact.get(
                    "content",
                    "",
                )
            )

            # ----------------------------------------------------
            # PATH VALIDATION
            # ----------------------------------------------------

            path = Path(path_string)

            if (
                not path_string
                or "\x00" in path_string
                or path.is_absolute()
                or "\\" in path_string
                or ".." in path.parts
                or "." in path.parts
                or "" in path.parts
                or (
                    len(path_string) > 1
                    and path_string[1] == ":"
                )
            ):

                findings.append(
                    {
                        "severity": "Critical",
                        "file": path_string[:500],
                        "issue": (
                            "Unsafe artifact path."
                        ),
                        "recommendation": (
                            "Use a normalized relative "
                            "POSIX-style artifact path."
                        ),
                    }
                )

                continue

            # ----------------------------------------------------
            # FILE SIZE
            # ----------------------------------------------------

            file_bytes = len(
                content.encode("utf-8")
            )

            total_bytes += file_bytes

            if file_bytes > MAX_FILE_BYTES:

                findings.append(
                    {
                        "severity": "Critical",
                        "file": path_string,
                        "issue": (
                            f"File exceeds the "
                            f"{MAX_FILE_BYTES}-byte limit."
                        ),
                        "recommendation": (
                            "Split or reduce the file."
                        ),
                    }
                )

                continue

            if (
                total_bytes
                > MAX_TOTAL_BYTES
            ):

                findings.append(
                    {
                        "severity": "Critical",
                        "file": None,
                        "issue": (
                            f"Total artifact size exceeds "
                            f"{MAX_TOTAL_BYTES} bytes."
                        ),
                        "recommendation": (
                            "Reduce the total generated source."
                        ),
                    }
                )

                break

            # ----------------------------------------------------
            # WRITE FILE
            # ----------------------------------------------------

            destination = (
                workspace / path
            )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            destination.write_text(
                content,
                encoding="utf-8",
            )

            materialized_files.append(
                (
                    path_string,
                    destination,
                )
            )

        # --------------------------------------------------------
        # ARTIFACT MATERIALIZATION CHECK
        # --------------------------------------------------------

        if not findings:

            checks.append(
                {
                    "name": "artifact-materialization",
                    "status": "passed",
                    "detail": (
                        "Artifacts safely materialized."
                    ),
                }
            )

        else:

            checks.append(
                {
                    "name": "artifact-materialization",
                    "status": "failed",
                    "detail": (
                        "One or more artifacts "
                        "could not be safely materialized."
                    ),
                }
            )

        # --------------------------------------------------------
        # PYTHON SYNTAX
        # --------------------------------------------------------

        python_files = [
            (path, file_path)
            for path, file_path
            in materialized_files
            if path.lower().endswith(".py")
        ]

        if python_files:

            python_failed = False

            for path, file_path in python_files:

                try:

                    source = file_path.read_text(
                        encoding="utf-8"
                    )

                    ast.parse(
                        source,
                        filename=path,
                    )

                except SyntaxError as exc:

                    python_failed = True

                    findings.append(
                        {
                            "severity": "High",
                            "file": path,
                            "issue": (
                                "Python syntax error: "
                                f"{exc.msg}"
                            ),
                            "recommendation": (
                                "Fix the Python syntax error."
                            ),
                        }
                    )

            checks.append(
                {
                    "name": "python-syntax",
                    "status": (
                        "failed"
                        if python_failed
                        else "passed"
                    ),
                    "detail": (
                        "Python files were parsed "
                        "without executing them."
                    ),
                }
            )

        # --------------------------------------------------------
        # JSON SYNTAX
        # --------------------------------------------------------

        json_files = [
            (path, file_path)
            for path, file_path
            in materialized_files
            if path.lower().endswith(".json")
        ]

        if json_files:

            json_failed = False

            for path, file_path in json_files:

                try:

                    source = file_path.read_text(
                        encoding="utf-8"
                    )

                    json.loads(source)

                except (
                    json.JSONDecodeError,
                    UnicodeDecodeError,
                ) as exc:

                    json_failed = True

                    findings.append(
                        {
                            "severity": "High",
                            "file": path,
                            "issue": (
                                "JSON syntax error: "
                                f"{str(exc)[:500]}"
                            ),
                            "recommendation": (
                                "Fix the JSON syntax."
                            ),
                        }
                    )

            checks.append(
                {
                    "name": "json-syntax",
                    "status": (
                        "failed"
                        if json_failed
                        else "passed"
                    ),
                    "detail": (
                        "JSON files were parsed "
                        "without executing them."
                    ),
                }
            )

        # --------------------------------------------------------
        # CREDENTIAL SCAN
        # --------------------------------------------------------

        credential_files = []

        for path, file_path in materialized_files:

            try:

                content = file_path.read_text(
                    encoding="utf-8"
                )

            except UnicodeDecodeError:
                continue

            if any(
                pattern.search(content)
                for pattern in SECRET_PATTERNS
            ):

                credential_files.append(
                    path
                )

        if credential_files:

            for path in credential_files:

                findings.append(
                    {
                        "severity": "Critical",
                        "file": path,
                        "issue": (
                            "A value resembling a "
                            "hard-coded credential was found."
                        ),
                        "recommendation": (
                            "Remove the credential and use "
                            "managed identity or an approved "
                            "secret-management mechanism."
                        ),
                    }
                )

            checks.append(
                {
                    "name": "credential-scan",
                    "status": "failed",
                    "detail": (
                        f"Potential credentials found "
                        f"in {len(credential_files)} file(s)."
                    ),
                }
            )

        else:

            checks.append(
                {
                    "name": "credential-scan",
                    "status": "passed",
                    "detail": (
                        "No obvious credential-like "
                        "literals were detected."
                    ),
                }
            )

        # --------------------------------------------------------
        # TEST FILE CHECK
        # --------------------------------------------------------

        has_tests = any(
            (
                path.lower().startswith("test/")
                or path.lower().startswith("tests/")
                or "/test" in path.lower()
                or path.lower().startswith("test_")
            )
            for path, _ in materialized_files
        )

        checks.append(
            {
                "name": "test-files",
                "status": (
                    "passed"
                    if has_tests
                    else "warning"
                ),
                "detail": (
                    "Test source files detected."
                    if has_tests
                    else "No test source file detected."
                ),
            }
        )

        if not has_tests:

            findings.append(
                {
                    "severity": "Medium",
                    "file": None,
                    "issue": (
                        "No test source file was generated."
                    ),
                    "recommendation": (
                        "Add tests for the approved "
                        "acceptance criteria."
                    ),
                }
            )

        # --------------------------------------------------------
        # FINAL STATUS
        # --------------------------------------------------------

        critical_or_high = any(
            finding["severity"]
            in {
                "Critical",
                "High",
            }
            for finding in findings
        )

        status = (
            "failed"
            if critical_or_high
            else "passed"
        )

        summary = (
            "Sandbox source checks passed. Application compilation and test execution were not performed."
            if status == "passed"
            else
            "Sandbox source checks found blocking issues. Application compilation and test execution were not performed."
        )

        return {
            "contractVersion": "1",
            "status": status,
            "summary": summary,
            "checks": checks,
            "findings": findings[:100],
        }

    finally:

        shutil.rmtree(
            workspace,
            ignore_errors=True,
        )


# ================================================================
# JOB MODE
# ================================================================

def get_job_credential():

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


def get_storage_account() -> str:

    value = os.getenv(
        "AUTOFORGE_SANDBOX_STORAGE_ACCOUNT",
        "afstorage5usl4p",
    ).strip()

    if not value:

        raise RuntimeError(
            "AUTOFORGE_SANDBOX_STORAGE_ACCOUNT "
            "is not configured."
        )

    return value


def get_storage_container() -> str:

    value = os.getenv(
        "AUTOFORGE_SANDBOX_STORAGE_CONTAINER",
        "sandbox-runs",
    ).strip()

    if not value:

        raise RuntimeError(
            "AUTOFORGE_SANDBOX_STORAGE_CONTAINER "
            "is not configured."
        )

    return value


def download_contract(
    run_id: str,
) -> dict[str, Any]:

    credential = get_job_credential()

    try:

        account = get_storage_account()

        container_name = get_storage_container()

        service = BlobServiceClient(
            account_url=(
                f"https://{account}"
                ".blob.core.windows.net"
            ),
            credential=credential,
        )

        try:

            container = (
                service.get_container_client(
                    container_name
                )
            )

            blob = container.get_blob_client(
                f"{run_id}/contract.json"
            )

            downloader = blob.download_blob()

            content = downloader.readall()

            if len(content) > MAX_RESULT_BYTES:

                raise RuntimeError(
                    "Contract exceeds maximum allowed size."
                )

            data = json.loads(
                content.decode("utf-8")
            )

            if not isinstance(
                data,
                dict,
            ):

                raise RuntimeError(
                    "Contract must be a JSON object."
                )

            return data

        finally:

            service.close()

    finally:

        credential.close()


def upload_result(
    run_id: str,
    result: dict[str, Any],
) -> None:

    credential = get_job_credential()

    try:

        account = get_storage_account()

        container_name = get_storage_container()

        service = BlobServiceClient(
            account_url=(
                f"https://{account}"
                ".blob.core.windows.net"
            ),
            credential=credential,
        )

        try:

            container = (
                service.get_container_client(
                    container_name
                )
            )

            blob = container.get_blob_client(
                f"{run_id}/result.json"
            )

            payload = json.dumps(
                result,
                ensure_ascii=False,
            ).encode("utf-8")

            if len(payload) > MAX_RESULT_BYTES:

                raise RuntimeError(
                    "Result exceeds maximum allowed size."
                )

            blob.upload_blob(
                payload,
                overwrite=True,
            )

        finally:

            service.close()

    finally:

        credential.close()


def run_job() -> int:

    run_id = os.getenv(
        "AUTOFORGE_RUN_ID",
        "",
    ).strip()

    if not run_id:

        print(
            "ERROR: AUTOFORGE_RUN_ID is not configured.",
            flush=True,
        )

        return 1

    print(
        f"AutoForge sandbox job started: {run_id}",
        flush=True,
    )

    try:

        # --------------------------------------------------------
        # DOWNLOAD CONTRACT
        # --------------------------------------------------------

        print(
            "Downloading contract...",
            flush=True,
        )

        contract = download_contract(
            run_id
        )

        print(
            "Contract downloaded.",
            flush=True,
        )

        # --------------------------------------------------------
        # VALIDATE CONTRACT
        # --------------------------------------------------------

        result = validate_contract(
            contract
        )

        # --------------------------------------------------------
        # ADD RUN ID
        # --------------------------------------------------------

        result["runId"] = run_id

        # --------------------------------------------------------
        # UPLOAD RESULT
        # --------------------------------------------------------

        print(
            "Uploading validation result...",
            flush=True,
        )

        upload_result(
            run_id,
            result,
        )

        print(
            "Validation result uploaded.",
            flush=True,
        )

        print(
            f"Sandbox status: {result['status']}",
            flush=True,
        )

        # --------------------------------------------------------
        # IMPORTANT
        #
        # Validation failure is NOT infrastructure failure.
        #
        # Therefore:
        #
        # passed validation -> exit 0
        # failed validation -> exit 0
        #
        # Backend gets the actual status from result.json.
        #
        # Only infrastructure errors return 1.
        # --------------------------------------------------------

        return 0

    except Exception as exc:

        print(
            "Sandbox Job infrastructure error:",
            flush=True,
        )

        print(
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        # Try to write an infrastructure failure result.
        try:

            error_result = {
                "contractVersion": "1",
                "runId": run_id,
                "status": "failed",
                "summary": (
                    "Sandbox runner infrastructure failure."
                ),
                "checks": [
                    {
                        "name": "runner",
                        "status": "failed",
                        "detail": (
                            f"{type(exc).__name__}: {str(exc)[:500]}"
                        ),
                    }
                ],
                "findings": [
                    {
                        "severity": "Critical",
                        "file": None,
                        "issue": (
                            "Sandbox runner failed before "
                            "validation completed."
                        ),
                        "recommendation": (
                            "Inspect the Container Apps Job logs."
                        ),
                    }
                ],
            }

            upload_result(
                run_id,
                error_result,
            )

        except Exception as upload_exc:

            print(
                "Could not upload failure result: "
                f"{type(upload_exc).__name__}: "
                f"{upload_exc}",
                flush=True,
            )

        return 1


# ================================================================
# APPLICATION ENTRYPOINT
# ================================================================

if __name__ == "__main__":

    job_mode = (
        os.getenv(
            "AUTOFORGE_JOB_MODE",
            "false",
        ).lower()
        == "true"
    )

    if job_mode:

        exit_code = run_job()

        sys.exit(exit_code)

    # ------------------------------------------------------------
    # NORMAL HTTP SERVER MODE
    # ------------------------------------------------------------

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
    )
