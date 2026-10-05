"""Normalize known invalid startup patterns before artifacts are reviewed."""

import json
import re


def normalize_startup(files: dict[str, str]) -> dict[str, str]:
    files = dict(files)
    for path, content in list(files.items()):
        if path.rsplit("/", 1)[-1] != "package.json":
            continue
        try:
            package = json.loads(content)
        except ValueError:
            continue
        if not isinstance(package, dict):
            continue
        scripts = package.get("scripts", {})
        dependencies = package.get("dependencies", {})
        dev_dependencies = package.get("devDependencies", {})
        if not all(isinstance(item, dict) for item in (scripts, dependencies, dev_dependencies)):
            continue
        root = path.rsplit("/", 1)[0] + "/" if "/" in path else ""
        # Complete a declared CRA build only when no lockfile needs updating.
        if (any(isinstance(script, str) and re.match(r"^react-scripts\s", script) for script in scripts.values())
                and "react-scripts" not in dependencies and "react-scripts" not in dev_dependencies
                and root + "package-lock.json" not in files and root + "npm-shrinkwrap.json" not in files):
            package["devDependencies"] = {**dev_dependencies, "react-scripts": "5.0.1"}
            files[path] = json.dumps(package, indent=2) + "\n"
    # Pydantic's EmailStr loads this optional dependency at model creation.
    for path, requirements in list(files.items()):
        if path.rsplit("/", 1)[-1] != "requirements.txt":
            continue
        root = path.rsplit("/", 1)[0] + "/" if "/" in path else ""
        uses_email = any(
            name.startswith(root) and name.endswith(".py")
            and re.search(r"(?m)^from pydantic import [^\n]*\bEmailStr\b", source)
            for name, source in files.items()
        )
        has_dependency = re.search(
            r"(?im)^\s*(?:email[-_]validator\b|pydantic\[[^\]]*email[^\]]*\]|fastapi\[[^\]]*(?:standard|all)[^\]]*\])",
            requirements,
        )
        if uses_email and not has_dependency:
            files[path] = requirements.rstrip() + "\nemail-validator\n"
    dockerfile = files.get("Dockerfile", "")
    # Only normalize standalone installs. Compound commands and flags retain
    # their authored semantics. Never fall back after a locked install fails.
    dockerfile = re.sub(
        r"(?m)^RUN npm ci\s*$",
        "RUN if [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then npm ci; else npm install; fi",
        dockerfile,
    )
    stages = list(re.finditer(r"(?im)^FROM\s+([^\s]+)[^\n]*", dockerfile))
    if not stages:
        return files
    final = stages[-1]
    python_image = final[1].lower().startswith("python:")
    prefix, body = dockerfile[:final.end()], dockerfile[final.end():]

    def fix_shell(command: str) -> str:
        if python_image:
            # Match command position only; never rewrite echoes or string data.
            command = re.sub(r"(^|[;&|]\s*)(exec\s+)?uvicorn\s+", r"\1\2python -m uvicorn ", command)
        # Nginx already stays foreground with -g 'daemon off;'.
        command = re.sub(
            r"(\bnginx\s+-g\s+(['\"])daemon off;\2)\s+--no-daemon\b",
            r"\1", command,
        )
        return command

    def fix_instruction(match: re.Match) -> str:
        instruction, value = match[1], match[2]
        try:
            args = json.loads(value)
        except ValueError:
            return instruction + " " + fix_shell(value)
        if not isinstance(args, list) or not args or not all(isinstance(arg, str) for arg in args):
            return match[0]
        if python_image and args[0] == "uvicorn":
            args = ["python", "-m", *args]
        elif len(args) == 3 and args[0] in {"sh", "/bin/sh", "bash", "/bin/bash"} and args[1] == "-c":
            args[2] = fix_shell(args[2])
        elif args == ["nginx", "-g", "daemon off;", "--no-daemon"]:
            args.pop()
        return instruction + " " + json.dumps(args)

    corrected = re.sub(r"(?m)^(CMD|ENTRYPOINT)\s+([^\n]+)$", fix_instruction, body)
    return {**files, "Dockerfile": prefix + corrected}
