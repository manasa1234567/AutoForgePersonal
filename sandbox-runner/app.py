"""HTTP adapter and bounded project checks for ACA custom session containers.

The submitted project is untrusted. This process runs as an unprivileged user,
in an ACA session container with network egress disabled, and applies per-command
resource limits. It never installs dependencies or fetches code from the network.
"""
from __future__ import annotations

import ast
import json
import os
import re
import selectors
import signal
import subprocess
import tempfile
import time
from pathlib import Path, PurePosixPath
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

MAX_REQUEST_BYTES = 1_000_000
MAX_FILES = 128
MAX_FILE_BYTES = 30_000
MAX_TOTAL_BYTES = 100_000
MAX_OUTPUT_CHARS = 4_000
DEFAULT_TIMEOUT = 120
MAX_TIMEOUT = 600

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


class InvalidInput(ValueError):
    pass


def _safe_path(raw: Any) -> PurePosixPath:
    if not isinstance(raw, str) or not raw or "\x00" in raw or "\\" in raw:
        raise InvalidInput("Artifact paths must be normalized relative paths.")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in raw.split("/")) or re.match(r"^[A-Za-z]:", raw):
        raise InvalidInput("Artifact paths must be normalized relative paths.")
    if len(raw) > 240:
        raise InvalidInput("An artifact path exceeds 240 characters.")
    return path


def _validate_payload(payload: Any) -> tuple[dict[str, str], int]:
    if not isinstance(payload, dict) or payload.get("contractVersion") != "1":
        raise InvalidInput("Request must use contractVersion '1'.")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise InvalidInput("Request must contain a non-empty artifacts object.")
    if len(artifacts) > MAX_FILES:
        raise InvalidInput(f"Artifact count exceeds the {MAX_FILES}-file limit.")

    timeout = payload.get("timeoutSeconds", DEFAULT_TIMEOUT)
    if isinstance(timeout, bool) or not isinstance(timeout, int) or not 5 <= timeout <= MAX_TIMEOUT:
        raise InvalidInput(f"timeoutSeconds must be an integer from 5 to {MAX_TIMEOUT}.")

    clean: dict[str, str] = {}
    total = 0
    for raw_path, content in artifacts.items():
        path = _safe_path(raw_path)
        if not isinstance(content, str):
            raise InvalidInput(f"Artifact {raw_path!r} must contain text.")
        size = len(content.encode("utf-8"))
        if size > MAX_FILE_BYTES:
            raise InvalidInput(f"Artifact {raw_path!r} exceeds the {MAX_FILE_BYTES}-byte file limit.")
        total += size
        if total > MAX_TOTAL_BYTES:
            raise InvalidInput(f"Combined artifacts exceed the {MAX_TOTAL_BYTES}-byte limit.")
        clean[path.as_posix()] = content
    return clean, timeout


def _write_artifacts(root: Path, artifacts: dict[str, str]) -> None:
    for name, content in artifacts.items():
        destination = root.joinpath(*PurePosixPath(name).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8", newline="")


def _limit_child() -> None:
    """Set Linux limits in the child immediately before exec."""
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (MAX_TIMEOUT, MAX_TIMEOUT + 1))
    resource.setrlimit(resource.RLIMIT_FSIZE, (25 * 1024 * 1024, 25 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    # ACA also enforces the container memory limit; this caps a single process.
    memory = 1536 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))


def _run(argv: list[str], cwd: Path, deadline: float) -> tuple[int, str]:
    output = bytearray()
    try:
        process = subprocess.Popen(
            ["setpriv", "--no-new-privs", "--reuid", "10002", "--regid", "10002", "--clear-groups", "--", *argv],
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            close_fds=True,
            start_new_session=True,
            preexec_fn=_limit_child,
            env={
                "PATH": "/opt/runner-venv/bin:/usr/local/bin:/usr/bin:/bin",
                "HOME": str(cwd / ".runner-home"),
                "TMPDIR": str(cwd / ".runner-tmp"),
                "CI": "true",
                "LANG": "C.UTF-8",
                "npm_config_offline": "true",
                "PIP_NO_INDEX": "1",
            },
        )
        assert process.stdout is not None
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while selector.get_map():
                if time.monotonic() >= deadline:
                    raise subprocess.TimeoutExpired(argv, timeout=MAX_TIMEOUT)
                for key, _ in selector.select(timeout=min(0.2, max(0.01, deadline - time.monotonic()))):
                    chunk = os.read(key.fd, 4096)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    if len(output) < MAX_OUTPUT_CHARS * 4:
                        output.extend(chunk[: MAX_OUTPUT_CHARS * 4 - len(output)])
                if process.poll() is not None and not selector.select(timeout=0):
                    # Drain EOF on the next loop before exiting.
                    continue
        return process.wait(), output.decode("utf-8", errors="replace")[-MAX_OUTPUT_CHARS:]
    except subprocess.TimeoutExpired:
        if "process" in locals():
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if process.poll() is None:
                process.wait()
        return 124, output.decode("utf-8", errors="replace")[-MAX_OUTPUT_CHARS:] + "\nCommand timed out."
    except OSError as exc:
        if "process" in locals() and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        return 127, f"Could not start the configured check: {type(exc).__name__}: {exc}"


def _finding(severity: str, issue: str, recommendation: str, file: str | None = None) -> dict[str, Any]:
    return {"severity": severity, "file": file, "issue": issue[:1000], "recommendation": recommendation[:1000]}


def validate_project(root: Path, artifacts: dict[str, str], timeout: int) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    findings: list[dict[str, Any]] = []
    deadline = time.monotonic() + timeout
    runnable = False

    python_files = [(name, content) for name, content in artifacts.items() if name.lower().endswith(".py")]
    if python_files:
        syntax_ok = True
        for name, content in python_files:
            try:
                ast.parse(content, filename=name)
            except SyntaxError as exc:
                syntax_ok = False
                findings.append(_finding("High", f"Python syntax error at line {exc.lineno}: {exc.msg}", "Correct the syntax error and rerun validation.", name))
        checks.append({"name": "python_syntax", "status": "passed" if syntax_ok else "failed", "detail": f"Parsed {len(python_files)} Python file(s)."})

        test_files = [name for name in artifacts if re.search(r"(^|/)(tests?/|test_[^/]+\.py$|[^/]+_test\.py$)", name)]
        if test_files:
            runnable = True
            code, output = _run(["python", "-m", "pytest", "-q", *test_files], root, deadline)
            checks.append({"name": "python_tests", "status": "passed" if code == 0 else "failed", "detail": output or f"pytest exited with status {code}."})
            if code != 0:
                findings.append(_finding("High", "Python tests failed or require dependencies that are not present in the offline runner image.", "Use only dependencies available in the runner image, or add an approved offline dependency source before enabling validation."))
        else:
            checks.append({"name": "python_tests", "status": "skipped", "detail": "No Python test files were supplied."})

    package_files = [(name, content) for name, content in artifacts.items() if PurePosixPath(name).name == "package.json"]
    if package_files:
        package_ok = True
        for name, content in package_files:
            try:
                package = json.loads(content)
                if not isinstance(package, dict):
                    raise ValueError("package.json must contain an object")
            except (ValueError, TypeError) as exc:
                package_ok = False
                findings.append(_finding("High", f"Invalid package.json: {exc}", "Correct package.json syntax and rerun validation.", name))
                continue
            scripts = package.get("scripts", {})
            if not isinstance(scripts, dict):
                scripts = {}
            package_root = root.joinpath(*PurePosixPath(name).parent.parts)
            for script, check_name in (("build", "node_build"), ("test", "node_tests")):
                if script not in scripts:
                    checks.append({"name": check_name, "status": "skipped", "detail": f"No {script} script is declared."})
                    continue
                runnable = True
                # This intentionally executes generated project code inside the isolated,
                # unprivileged, no-egress ACA session. It never installs dependencies.
                code, output = _run(["npm", "run", script, "--if-present"], package_root, deadline)
                checks.append({"name": check_name, "status": "passed" if code == 0 else "failed", "detail": output or f"npm run {script} exited with status {code}."})
                if code != 0:
                    findings.append(_finding("High", f"Node {script} check failed; dependencies are not installed or the project check returned an error.", "Provide dependencies through an approved offline source and fix the reported check before retrying.", name))
        checks.append({"name": "package_json", "status": "passed" if package_ok else "failed", "detail": f"Parsed {len(package_files)} package.json file(s)."})

    json_files = [(name, content) for name, content in artifacts.items() if name.lower().endswith(".json") and PurePosixPath(name).name != "package.json"]
    if json_files:
        valid = True
        for name, content in json_files:
            try:
                json.loads(content)
            except ValueError as exc:
                valid = False
                findings.append(_finding("High", f"Invalid JSON: {str(exc)[:300]}", "Correct the JSON syntax and rerun validation.", name))
        checks.append({"name": "json_syntax", "status": "passed" if valid else "failed", "detail": f"Parsed {len(json_files)} JSON file(s)."})

    unsupported_manifests = [
        name for name in artifacts
        if PurePosixPath(name).name.lower() in {"pom.xml", "build.gradle", "build.gradle.kts", "go.mod", "cargo.toml"}
    ]
    if unsupported_manifests:
        checks.append({"name": "unsupported_runtime", "status": "failed", "detail": "The runner cannot build one or more detected project runtimes."})
        for name in unsupported_manifests[:10]:
            findings.append(_finding("High", "This runner image does not include an offline build policy for this project runtime.", "Extend the runner image and policy for this runtime before using it for release validation.", name))

    if not checks:
        checks.append({"name": "supported_project", "status": "failed", "detail": "The runner found no supported Python or Node project manifest/source files."})
        findings.append(_finding("High", "This runner supports Python projects and Node projects with package.json; no supported project files were found.", "Use a supported runtime or extend the runner with a reviewed, offline-compatible validation policy."))
    elif not runnable:
        findings.append(_finding("High", "No executable test or build check was available; syntax checks alone cannot pass runtime validation.", "Add Python tests or Node build/test scripts and ensure their dependencies are available offline."))

    failed = any(check["status"] == "failed" for check in checks) or not runnable
    status = "failed" if failed else "passed"
    summary = "Offline build/test checks completed." if status == "passed" else "Runtime validation did not pass; see checks and findings."
    return {"contractVersion": "1", "status": status, "summary": summary, "checks": checks, "findings": findings}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "contractVersion": "1"}


@app.post("/autoforge/validate")
async def validate(request: Request) -> JSONResponse:
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_REQUEST_BYTES:
        return JSONResponse({"detail": "Request exceeds the 1 MB limit."}, status_code=413)
    body = await request.body()
    if len(body) > MAX_REQUEST_BYTES:
        return JSONResponse({"detail": "Request exceeds the 1 MB limit."}, status_code=413)
    try:
        payload = json.loads(body)
        artifacts, timeout = _validate_payload(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JSONResponse({"detail": "Request body must be valid JSON."}, status_code=400)
    except InvalidInput as exc:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    with tempfile.TemporaryDirectory(prefix="autoforge-") as temp_dir:
        root = Path(temp_dir)
        try:
            _write_artifacts(root, artifacts)
            (root / ".runner-home").mkdir(mode=0o700)
            (root / ".runner-tmp").mkdir(mode=0o700)
            # One ACA session is dedicated to this request. Make only its temp
            # workspace writable by the dropped-privilege child process.
            for current, directories, files in os.walk(root):
                os.chmod(current, 0o777)
                for filename in files:
                    os.chmod(Path(current) / filename, 0o666)
            result = validate_project(root, artifacts, timeout)
        except Exception as exc:  # Do not leak stack traces or container paths to callers.
            result = {
                "contractVersion": "1",
                "status": "failed",
                "summary": "Runner could not safely complete validation.",
                "checks": [{"name": "runner", "status": "failed", "detail": type(exc).__name__}],
                "findings": [_finding("High", "The sandbox runner encountered an internal validation error.", "Inspect the session container logs and correct the runner configuration.")],
            }
    return JSONResponse(result)
