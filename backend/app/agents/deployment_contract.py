"""Checks provable from source; container startup is verified by the image preflight."""

import json
import posixpath
import re
import shlex


def missing_copy_sources(artifacts: dict[str, str]) -> list[str]:
    """Find missing literal build-context COPY inputs, without guessing image paths.

    Stage copies, variables, globs and heredocs need Docker's interpretation.
    In particular, a Uvicorn module path cannot be compared with repository paths:
    WORKDIR, COPY, stage inheritance and PYTHONPATH can all change its location.
    """
    missing = []
    dockerfile = re.sub(r"\\\r?\n", " ", artifacts.get("Dockerfile", ""))
    for line in dockerfile.splitlines():
        match = re.match(r"(?i)^\s*COPY\s+(.+)$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if re.search(r"--from(?:=|\s)", value) or "<<" in value:
            continue
        # Unknown flag syntax is left to Docker rather than rejected here.
        value = re.sub(r"^(?:--[\w-]+(?:=[^\s]+)?\s+)+", "", value)
        try:
            parts = json.loads(value) if value.startswith("[") else shlex.split(value)
        except (ValueError, TypeError):
            continue
        if not isinstance(parts, list) or len(parts) < 2:
            continue
        for source in parts[:-1]:
            if not isinstance(source, str) or any(char in source for char in "$*?["):
                continue
            source = posixpath.normpath(source.lstrip("/"))
            if source == "." or source in artifacts:
                continue
            if any(path.startswith(source.rstrip("/") + "/") for path in artifacts):
                continue
            if source not in missing:
                missing.append(source)
    return missing
