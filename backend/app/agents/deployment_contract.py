"""Checks provable from source; container startup is verified by the image preflight."""

import json
import posixpath
import re
import shlex
from .python_import_contract import local_import_issues


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


def stage_copy_issues(artifacts: dict[str, str]) -> list[str]:
    """Recognize misplaced copies of literal directories in earlier stages.

    This is deliberately not a Docker interpreter. Only track local directory
    COPY instructions with explicit WORKDIR, and invalidate that evidence after
    RUN/ADD or unsupported syntax. Build outputs and external images are left
    to Docker. Never compare a container import path with a repository path.
    """
    stages: dict[str, set[str]] = {}
    opaque_stages: set[int] = set()
    known: set[str] = set()
    workdir: str | None = None
    stage_number = -1
    issues: list[str] = []
    dockerfile = re.sub(r"\\\r?\n", " ", artifacts.get("Dockerfile", ""))
    for line in dockerfile.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        instruction, _, value = line.partition(" ")
        instruction = instruction.upper()
        value = value.strip()
        if instruction == "FROM":
            stage_number += 1
            known = set()
            workdir = None
            stages[str(stage_number)] = known
            alias = re.search(r"(?i)\sAS\s+(\S+)\s*$", value)
            if alias:
                stages[alias.group(1).lower()] = known
        elif instruction == "WORKDIR":
            if "$" in value or not value:
                workdir = None
            elif value.startswith("/") or workdir:
                workdir = posixpath.normpath(posixpath.join(workdir or "/", value))
        elif instruction in {"RUN", "ADD", "ONBUILD"}:
            # Commands can create, move or delete directories: stop inferring.
            known.clear()
            # A dependency-only pip command before source copying is common.
            # Other commands may create a second valid source directory.
            if instruction != "RUN" or not re.fullmatch(
                r"(?:python(?:3)? -m )?pip(?:3)? install [\w./=\[\],+ :@-]+", value
            ):
                opaque_stages.add(id(known))
        elif instruction == "COPY":
            from_match = re.match(r"--from=([^\s]+)\s+", value)
            copy_value = value[from_match.end():] if from_match else value
            if copy_value.startswith("--") or any(c in copy_value for c in "$*?<<"):
                known.clear()
                continue
            try:
                parts = json.loads(copy_value) if copy_value.startswith("[") else shlex.split(copy_value)
            except ValueError:
                known.clear()
                continue
            if not isinstance(parts, list) or len(parts) != 2 or not all(isinstance(p, str) for p in parts):
                known.clear()
                continue
            source, destination = parts
            if from_match:
                earlier = stages.get(from_match.group(1).lower(), set())
                source_path = posixpath.normpath("/" + source.lstrip("/"))
                candidates = [path for path in earlier if posixpath.basename(path) == posixpath.basename(source_path)]
                if id(earlier) not in opaque_stages and source_path not in earlier and len(candidates) == 1:
                    issues.append(
                        f"COPY --from={from_match.group(1)} requests {source_path}, "
                        f"but the source directory was copied to {candidates[0]} in that stage. "
                        "Use the actual stage path or explicitly create the requested path."
                    )
                continue
            source_path = posixpath.normpath(source.lstrip("/"))
            prefix = "" if source_path == "." else source_path + "/"
            if workdir and any(path.startswith(prefix) for path in artifacts) and source_path not in artifacts:
                target = posixpath.normpath(posixpath.join(workdir, destination))
                known.add(target)
                # Directory COPY includes nested directories as well.
                for path in artifacts:
                    if not path.startswith(prefix):
                        continue
                    relative = posixpath.dirname(path[len(prefix):])
                    while relative:
                        known.add(posixpath.join(target, relative))
                        relative = posixpath.dirname(relative)
    return issues


def packaging_issues(artifacts: dict[str, str]) -> list[str]:
    return [
        f"Dockerfile COPY requires missing project source: {source}."
        for source in missing_copy_sources(artifacts)
    ] + stage_copy_issues(artifacts) + dependency_manifest_issues(artifacts) + local_import_issues(artifacts) + uncopied_startup_issues(artifacts)


def uncopied_startup_issues(artifacts: dict[str, str]) -> list[str]:
    """Catch supplied ASGI source omitted from every literal COPY instruction.

    Do not infer image paths: a copy in any stage counts, even if relocated.
    Dynamic inputs, ADD and generated source require actual image validation.
    """
    dockerfile = re.sub(r"\\\r?\n", " ", artifacts.get("Dockerfile", ""))
    final_stage = re.split(r"(?im)(?=^\s*FROM\s)", dockerfile)[-1]
    commands = re.findall(r"(?im)^\s*(?:CMD|ENTRYPOINT)\s+(\[.*\])\s*$", final_stage)
    args = []
    for command in commands:
        try:
            parsed = json.loads(command)
        except ValueError:
            return []
        if not isinstance(parsed, list) or not all(isinstance(arg, str) for arg in parsed):
            return []
        args.extend(parsed)
    if not any(arg in {"uvicorn", "hypercorn"} for arg in args):
        return []
    modules = [arg.split(":")[0] for arg in args if re.fullmatch(r"[\w.]+:[\w.]+", arg)]
    if len(modules) != 1:
        return []
    suffix = modules[0].replace(".", "/")
    candidates = [path for path in artifacts if any(
        path == name or path.endswith("/" + name)
        for name in (suffix + ".py", suffix + "/__init__.py")
    )]
    if not candidates:
        return []  # Installed/external modules are checked by real startup.
    sources = []
    for line in dockerfile.splitlines():
        if re.match(r"(?i)^\s*(?:ADD|ONBUILD)\s", line):
            return []
        match = re.match(r"(?i)^\s*COPY\s+(.+)$", line)
        if not match:
            continue
        value = match[1].strip()
        if re.search(r"--from(?:=|\s)", value):
            continue
        if any(char in value for char in "$*?[<") and not value.startswith("["):
            return []
        value = re.sub(r"^(?:--[\w-]+(?:=[^\s]+)?\s+)+", "", value)
        try:
            parts = json.loads(value) if value.startswith("[") else shlex.split(value)
        except (ValueError, TypeError):
            return []
        if not isinstance(parts, list) or len(parts) < 2 or not all(isinstance(p, str) for p in parts):
            return []
        for source in parts[:-1]:
            if any(char in source for char in "$*?[<"):
                return []
            sources.append(posixpath.normpath(source.lstrip("/")))
    if any(source == "." or path == source or path.startswith(source.rstrip("/") + "/")
           for source in sources for path in candidates):
        return []
    return [
        f"Dockerfile starts local ASGI module {modules[0]}, but its source ({', '.join(candidates)}) "
        "is not included in any build-context COPY. Copy the actual application source into the "
        "image, preserve its imports and align its final location with the startup command."
    ]


def dependency_manifest_issues(artifacts: dict[str, str]) -> list[str]:
    """Reject known incompatible declarations; do not rewrite versions or locks."""
    issues = []
    for path, content in artifacts.items():
        if path.rsplit("/", 1)[-1] != "package.json":
            continue
        try:
            package = json.loads(content)
        except ValueError:
            continue
        if not isinstance(package, dict):
            continue
        deps = package.get("dependencies", {})
        dev = package.get("devDependencies", {})
        if not isinstance(deps, dict) or not isinstance(dev, dict):
            continue
        combined = {**deps, **dev}
        cra = combined.get("react-scripts")
        ts = combined.get("typescript")
        scripts = package.get("scripts", {})
        uses_cra = isinstance(scripts, dict) and any(
            isinstance(command, str) and re.match(r"^\s*react-scripts(?:\s|$)", command)
            for command in scripts.values()
        )
        root = path.rsplit("/", 1)[0] + "/" if "/" in path else ""
        typed_sources = any(
            name.startswith(root + "src/") and name.endswith((".ts", ".tsx"))
            and not name.endswith(".d.ts")
            and not re.search(r"(?:^|/)(?:tests|__tests__)/|\.(?:test|spec)\.", name)
            for name in artifacts
        )
        if uses_cra and typed_sources:
            if root + "tsconfig.json" not in artifacts:
                issues.append(
                    f"{path}: react-scripts builds TypeScript sources but {root}tsconfig.json is missing. "
                    "Without that file CRA excludes .ts/.tsx from module resolution, so an existing "
                    "App.tsx can fail with Can't resolve './App'. Include a valid CRA TypeScript "
                    "configuration; do not rename or replace application source to hide this error."
                )
            missing = [name for name in ("typescript", "@types/react", "@types/react-dom") if not combined.get(name)]
            if missing:
                issues.append(
                    f"{path}: TypeScript react-scripts sources require declared build dependencies: "
                    f"{', '.join(missing)}. Use versions compatible with react-scripts and React "
                    "(react-scripts 5.0.1 requires TypeScript ^3.2.1 or ^4), update the lockfile, "
                    "and install build dependencies before compiling."
                )
        if uses_cra and not cra:
            issues.append(
                f"{path}: scripts invoke react-scripts but neither dependencies nor "
                "devDependencies declares it. npm install cannot provide this build tool. "
                "Declare a compatible react-scripts version and update the lockfile together. "
                "If using react-scripts 5.0.1, TypeScript must satisfy ^3.2.1 or ^4 "
                "(for example 4.9.5), not TypeScript 5. Install build dependencies before npm run build."
            )
        # Limit inference to simple exact/caret/tilde versions. Other semver
        # ranges, workspace references and overrides require the real resolver.
        if (isinstance(cra, str) and re.fullmatch(r"[~^]?5\.0\.1", cra.strip())
                and isinstance(ts, str) and re.fullmatch(r"[~^]?[5-9]\d*\.\d+\.\d+", ts.strip())):
            issues.append(
                f"{path}: react-scripts 5.0.1 requires TypeScript ^3.2.1 or ^4, "
                f"but typescript is {ts}. Select compatible dependencies and update any lockfile; "
                "do not use --force or --legacy-peer-deps to hide the conflict."
            )
    return issues
