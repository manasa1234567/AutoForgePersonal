"""Normalize known invalid startup patterns before artifacts are reviewed."""

import ast
import json
import re


def _mount_unserved_frontend(files: dict[str, str], final_stage: str) -> None:
    """Serve the packaged SPA for the known /app FastAPI frontend layout."""
    if re.findall(r"(?im)^WORKDIR\s+(\S+)\s*$", final_stage) != ["/app"]:
        return
    if re.search(r"(?im)^ENTRYPOINT\b", final_stage):
        return
    commands = re.findall(r"(?m)^CMD\s+([^\n]+)", final_stage)
    if len(commands) != 1:
        return
    try:
        command = json.loads(commands[0])
    except ValueError:
        command = commands[0].strip()
    if isinstance(command, list):
        valid_command = command[:4] in (
            ["python", "-m", "uvicorn", "app.main:app"],
            ["python", "-m", "uvicorn", "backend.app.main:app"],
        )
    else:
        valid_command = bool(re.match(
            r"^(?:exec\s+)?(?:python(?:3)?\s+-m\s+uvicorn|uvicorn)\s+(?:app|backend\.app)\.main:app(?:\s|$)",
            command,
        ))
    if not valid_command:
        return
    if not re.search(
        r"(?im)^COPY\s+--from=\S+\s+\S*dist/?\s+(?:\./|/app/)?frontend/dist/?\s*$",
        final_stage,
    ):
        return
    if "frontend/index.html" not in files:
        return
    path = "backend/app/main.py"
    source = files.get(path, "")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return
    if not any(isinstance(node, ast.ImportFrom) and node.module == "fastapi"
               and any(name.name == "FastAPI" and name.asname is None for name in node.names)
               for node in tree.body):
        return
    if not any(isinstance(node, ast.Assign) and len(node.targets) == 1
               and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "app"
               and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
               and node.value.func.id == "FastAPI" for node in tree.body):
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "app" and node.func.attr == "mount":
            mount = node.args[0] if node.args else next((kw.value for kw in node.keywords if kw.arg == "path"), None)
            if isinstance(mount, ast.Constant) and mount.value == "/":
                return
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "app" and node.func.attr in {"get", "api_route"}:
            route = node.args[0] if node.args else next((kw.value for kw in node.keywords if kw.arg == "path"), None)
            if not isinstance(route, ast.Constant) or not isinstance(route.value, str):
                return
            if "{" in route.value:
                return
    files[path] = source.rstrip() + (
        '\n\n# Serve the packaged UI at / while preserving API routes and static assets.\n'
        'from fastapi.responses import FileResponse as _AutoForgeFileResponse\n'
        'from fastapi.staticfiles import StaticFiles as _AutoForgeStaticFiles\n'
        '@app.middleware("http")\n'
        'async def _autoforge_serve_frontend_root(request, call_next):\n'
        '    if request.method == "GET" and request.url.path == "/":\n'
        '        return _AutoForgeFileResponse("/app/frontend/dist/index.html")\n'
        '    return await call_next(request)\n'
        'app.mount("/", _AutoForgeStaticFiles(directory="/app/frontend/dist", html=True), name="frontend")\n'
    )


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
        # This exact generated pin is unpublished. 4.0.4 is published and
        # declares Vite ^4.2.0 as its peer. Do not rewrite other versions/locks.
        vite = dev_dependencies.get("vite", dependencies.get("vite", ""))
        locked = any(root + name in files for name in (
            "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock", "bun.lockb"
        ))
        if isinstance(vite, str) and re.fullmatch(r"4\.(?:[2-9]|[1-9][0-9]+)\.\d+", vite) and not locked:
            for section in ("dependencies", "devDependencies"):
                if package.get(section, {}).get("@vitejs/plugin-react") == "4.0.9":
                    package[section]["@vitejs/plugin-react"] = "4.0.4"
                    files[path] = json.dumps(package, indent=2) + "\n"
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
            requirements = requirements.rstrip() + "\nemail-validator\n"
        fastapi_pin = re.search(
            r"(?im)^\s*fastapi(?:\[[^\]]+\])?\s*==\s*([0-9]+(?:\.[0-9]+){1,2})\b",
            requirements,
        )
        pydantic_pin = re.search(
            r"(?im)^\s*pydantic(?:\[[^\]]+\])?\s*==\s*([0-9]+(?:\.[0-9]+){1,2})\b",
            requirements,
        )
        if fastapi_pin and pydantic_pin:
            fastapi_version = tuple(int(part) for part in fastapi_pin.group(1).split("."))
            pydantic_version = pydantic_pin.group(1)
            incompatible_pair = fastapi_version < (0, 100) and int(pydantic_version.split(".", 1)[0]) >= 2
            unavailable_pin = pydantic_version == "2.1.2"
            if incompatible_pair or unavailable_pin:
                requirements = re.sub(
                    r"(?im)^(\s*fastapi(?:\[[^\]]+\])?\s*==)[^\s;#]+",
                    r"\g<1>0.115.12",
                    requirements,
                )
                requirements = re.sub(
                    r"(?im)^(\s*pydantic(?:\[[^\]]+\])?\s*==)[^\s;#]+",
                    r"\g<1>2.11.3",
                    requirements,
                )
        files[path] = requirements
    dockerfile = files.get("Dockerfile", "")
    # Vite's HTML entry is a build input, outside src/. Complete only the
    # explicit root-package layout; custom roots/stages keep their semantics.
    try:
        root_package = json.loads(files.get("package.json", "{}"))
    except ValueError:
        root_package = {}
    if (isinstance(root_package, dict) and isinstance(root_package.get("scripts"), dict)
            and root_package["scripts"].get("build") == "vite build" and "index.html" in files):
        sections = re.split(r"(?im)(?=^FROM\s)", dockerfile)
        for index, section in enumerate(sections):
            if (re.match(r"(?i)^FROM\s+node:", section)
                    and len(re.findall(r"(?im)^WORKDIR\s+", section)) == 1
                    and re.search(r"(?m)^COPY package\.json \.\s*$", section)
                    and re.search(r"(?m)^RUN npm run build\s*$", section)
                    and not re.search(r"(?im)^COPY[^\n]*(?:index\.html|\*)", section)
                    and not re.search(r"(?im)^COPY\s+\.\s", section)):
                sections[index] = re.sub(
                    r"(?m)^(COPY src \./src)[ \t]*$", r"\1\nCOPY index.html ./", section
                )
        dockerfile = "".join(sections)
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
    if python_image:
        _mount_unserved_frontend(files, corrected)
    return {**files, "Dockerfile": prefix + corrected}
