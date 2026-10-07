"""Normalize known invalid startup patterns before artifacts are reviewed."""

import ast
import json
import posixpath
import re
import shlex
from .poetry_packaging import resolve_poetry_before_install
from .python_optional_dependencies import uses_pydantic_email


def _copy_node_build_sources(files: dict[str, str], dockerfile: str) -> str:
    """Complete explicit manifest-only COPY layouts before a standalone build."""
    workdir = "/"
    manifests = {}
    directories = []
    output = []
    for line in dockerfile.splitlines():
        command, _, value = line.strip().partition(" ")
        if command.upper() == "FROM":
            workdir, manifests, directories = "/", {}, []
        elif command.upper() == "WORKDIR":
            workdir = posixpath.normpath(posixpath.join(workdir, value))
        elif command.upper() == "COPY" and not value.startswith("--") and not any(c in value for c in "$*\\"):
            try:
                parts = json.loads(value) if value.startswith("[") else shlex.split(value)
            except ValueError:
                parts = []
            if len(parts) == 2 and all(isinstance(p, str) for p in parts):
                source = posixpath.normpath(parts[0])
                destination = posixpath.normpath(posixpath.join(workdir, parts[1]))
                if posixpath.basename(source) == "package.json" and source in files:
                    target_dir = posixpath.dirname(destination) if destination.endswith("package.json") else destination
                    manifests[target_dir] = posixpath.dirname(source) or "."
                elif source == "." or any(p.startswith(source + "/") for p in files):
                    directories.append((source, destination))
        elif re.fullmatch(r"RUN\s+npm run build\s*", line.strip()):
            source = manifests.get(workdir)
            if source and "$" not in workdir:
                covered = any(
                    (source == src or src == "." or source.startswith(src + "/"))
                    and posixpath.normpath(posixpath.join(dest, posixpath.relpath(source, src))) == workdir
                    for src, dest in directories
                )
                prefix = "" if source == "." else source + "/"
                if not covered and any(p.startswith(prefix) and p.endswith(('.tsx', '.jsx', '.ts', '.js', '.html', '.vue', '.svelte')) for p in files):
                    output.append("COPY " + json.dumps([source + "/", "./"]))
                    directories.append((source, workdir))
        output.append(line)
    return "\n".join(output) + ("\n" if dockerfile.endswith("\n") else "")


def _normalize_generated_asgi_wrapper(files: dict[str, str], dockerfile: str) -> str:
    """Remove the known invalid multiline echo wrapper and run the real FastAPI app."""
    if "backend/app/main.py" not in files:
        return dockerfile
    pattern = re.compile(
        r'(?ms)^RUN\s+echo\s+"(?P<source>from fastapi import FastAPI\b.*?)"\s*>\s*main_combined\.py\s*$'
    )
    match = pattern.search(dockerfile)
    if not match:
        return dockerfile
    wrapper = match.group("source")
    if not all(marker in wrapper for marker in (
        "from app.main import app as api_app",
        "StaticFiles",
        "app.mount('/api', api_app)",
    )):
        return dockerfile
    if not re.search(r"(?im)^COPY\s+--from=\S+\s+\S+\s+/app/static/?\s*$", dockerfile):
        return dockerfile

    def replace_command(command_match: re.Match) -> str:
        try:
            command = json.loads(command_match.group(2))
        except ValueError:
            return command_match[0]
        if not isinstance(command, list) or "main_combined:app" not in command:
            return command_match[0]
        command = ["app.main:app" if item == "main_combined:app" else item for item in command]
        return command_match.group(1) + json.dumps(command)

    without_wrapper = dockerfile[:match.start()] + dockerfile[match.end():]
    rewritten = re.sub(r"(?m)^(CMD\s+)([^\n]+)$", replace_command, without_wrapper)
    if rewritten == without_wrapper:
        return dockerfile
    return rewritten


def _mount_unserved_frontend(files: dict[str, str], final_stage: str) -> None:
    """Serve a packaged SPA when a FastAPI image copies a frontend build."""
    workdirs = re.findall(r"(?im)^WORKDIR\s+(\S+)\s*$", final_stage)
    if workdirs != ["/app"]:
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
        if command[:3] == ["python", "-m", "uvicorn"] and len(command) > 3:
            app_target = command[3]
        elif command and command[0] == "uvicorn" and len(command) > 1:
            app_target = command[1]
        else:
            return
    else:
        match = re.match(
            r"^(?:exec\s+)?(?:python(?:3)?\s+-m\s+uvicorn|uvicorn)\s+([^\s]+)",
            command,
        )
        if not match:
            return
        app_target = match.group(1)
    module, separator, app_name = app_target.partition(":")
    if not separator or not module or app_name != "app":
        return
    static_directory = None
    for line in final_stage.splitlines():
        copy = re.match(r"(?i)^COPY\s+--from=\S+\s+\S+\s+(\S+)\s*$", line.strip())
        if not copy:
            continue
        raw_destination = copy.group(1)
        destination = posixpath.normpath(
            raw_destination if raw_destination.startswith("/")
            else posixpath.join(workdirs[-1], raw_destination)
        )
        parts = destination.strip("/").split("/")
        if "frontend" in parts and parts[-1] in {"build", "dist", "out"}:
            static_directory = destination
            break
        if parts[-1] == "static":
            static_directory = destination
            break
    if not static_directory:
        return
    if not any(
        path.startswith("frontend/") and path.endswith("index.html")
        for path in files
    ):
        return
    module_path = module.replace(".", "/") + ".py"
    matching_paths = [
        candidate for candidate in files
        if candidate == module_path or candidate.endswith("/" + module_path)
    ]
    if len(matching_paths) != 1:
        return
    path = matching_paths[0]
    source = files[path]
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
        f'        return _AutoForgeFileResponse({json.dumps(static_directory + "/index.html")})\n'
        '    return await call_next(request)\n'
        f'app.mount("/", _AutoForgeStaticFiles(directory={json.dumps(static_directory)}, html=True), name="frontend")\n'
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
        cra_build = any(
            isinstance(script, str) and re.match(r"^react-scripts(?:\s|$)", script)
            for script in scripts.values()
        )
        if cra_build and root + "public/index.html" not in files:
            files[root + "public/index.html"] = (
                '<!doctype html>\n<html lang="en">\n<head>\n'
                '  <meta charset="utf-8" />\n'
                '  <meta name="viewport" content="width=device-width, initial-scale=1" />\n'
                '  <title>Generated Application</title>\n'
                '</head>\n<body>\n  <noscript>This application requires JavaScript.</noscript>\n'
                '  <div id="root"></div>\n</body>\n</html>\n'
            )
    # Pydantic's EmailStr loads this optional dependency at model creation.
    for path, requirements in list(files.items()):
        if path.rsplit("/", 1)[-1] != "requirements.txt":
            continue
        root = path.rsplit("/", 1)[0] + "/" if "/" in path else ""
        uses_email = any(
            name.startswith(root) and name.endswith(".py")
            and uses_pydantic_email(source)
            for name, source in files.items()
        )
        has_dependency = re.search(
            r"(?im)^\s*(?:email[-_]validator\b|pydantic\[[^\]]*email[^\]]*\]|fastapi\[[^\]]*(?:standard|all)[^\]]*\])",
            requirements,
        )
        if uses_email and not has_dependency:
            requirements = requirements.rstrip() + "\nemail-validator\n"
        pydantic_v2 = bool(re.search(
            r"(?im)^\s*pydantic(?:\[[^\]]*\])?\s*(?:==|~=|>=|>)\s*2(?:\.|\s|$)",
            requirements,
        ))
        if pydantic_v2:
            for source_path, source in list(files.items()):
                if source_path.startswith(root) and source_path.endswith(".py"):
                    corrected = re.sub(
                        r"(\bconstr\s*\([^)]*?)\bregex\s*=",
                        r"\1pattern=",
                        source,
                    )
                    if corrected != source:
                        files[source_path] = corrected
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
    dockerfile = resolve_poetry_before_install(dockerfile)
    dockerfile = _copy_node_build_sources(files, dockerfile)
    dockerfile = _normalize_generated_asgi_wrapper(files, dockerfile)
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
