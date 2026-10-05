import json
from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.agents.coder_agent import CoderAgent
from app.agents.container_startup import normalize_startup


class ContainerStartupTests(unittest.TestCase):
    def frontend_fixture(self):
        return {
            "Dockerfile": 'FROM node:22 AS build\nFROM python:3.11-slim\nWORKDIR /app\n'
            'COPY --from=build /app/backend ./backend\n'
            'COPY --from=build /app/frontend/dist ./frontend/dist\n'
            'CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--port", "8080"]\nEXPOSE 8080\n',
            "frontend/index.html": '<div id="root"></div>',
            "backend/app/main.py": 'from fastapi import FastAPI\napp = FastAPI()\n'
            '@app.get("/hello")\ndef hello():\n    return {"message": "Hello World"}\n',
        }

    def test_packaged_frontend_served_without_changing_api(self):
        files = self.frontend_fixture()
        fixed = normalize_startup(files)
        self.assertNotIn("app.mount", files["backend/app/main.py"])
        self.assertEqual(normalize_startup(fixed), fixed)
        with tempfile.TemporaryDirectory() as folder:
            site = Path(folder)
            (site / "index.html").write_text('<h1>Hello UI</h1>', encoding="utf-8")
            (site / "assets").mkdir()
            (site / "assets" / "app.js").write_text('console.log("hello")', encoding="utf-8")
            namespace = {}
            # Execute only this controlled fixture, never downloaded artifacts.
            source = fixed["backend/app/main.py"].replace('"/app/frontend/dist"', repr(folder))
            exec(compile(source, "fixture.py", "exec"), namespace)
            with TestClient(namespace["app"]) as client:
                self.assertEqual(client.get("/").text, '<h1>Hello UI</h1>')
                self.assertEqual(client.get("/hello").json(), {"message": "Hello World"})
                self.assertEqual(client.get("/assets/app.js").status_code, 200)
                self.assertEqual(client.get("/missing").status_code, 404)

    def test_existing_routes_and_custom_layouts_are_unchanged(self):
        for extra in [
            '@app.get("/")\ndef root():\n    return "existing"\n',
            'app.mount("/", static_app)\n',
            'app.include_router(router)\n',
            '@app.get("/{path:path}")\ndef fallback(path):\n    return path\n',
        ]:
            files = self.frontend_fixture()
            files["backend/app/main.py"] += extra
            self.assertEqual(normalize_startup(files), files)
        for change in [
            lambda value: value.replace("WORKDIR /app", "WORKDIR /srv"),
            lambda value: value.replace("./frontend/dist", "./public"),
            lambda value: value + 'ENTRYPOINT ["custom"]\n',
            lambda value: value.replace("backend.app.main:app", "custom:app"),
        ]:
            files = self.frontend_fixture()
            files["Dockerfile"] = change(files["Dockerfile"])
            self.assertEqual(normalize_startup(files), files)

    def test_missing_lockfile_and_cra_tool_are_handled_together(self):
        original = {
            "Dockerfile": "FROM node:18\nRUN npm ci\nEXPOSE 8080\n",
            "package.json": json.dumps({"scripts": {"build": "react-scripts build"}, "dependencies": {"react": "18.2.0"}}),
        }
        fixed = CoderAgent._validate_deployment_contract(original)
        self.assertIn("then npm ci; else npm install; fi", fixed["Dockerfile"])
        self.assertEqual(json.loads(fixed["package.json"])["devDependencies"]["react-scripts"], "5.0.1")
        self.assertEqual(normalize_startup(fixed), fixed)

    def test_locked_manifest_and_custom_install_flags_are_preserved(self):
        files = {"Dockerfile": "FROM node:22\nRUN npm ci --omit=dev\n",
                 "package.json": '{"scripts":{"build":"react-scripts build"}}',
                 "package-lock.json": '{}'}
        self.assertEqual(normalize_startup(files), files)

    def test_actual_failed_command_is_corrected_before_review(self):
        command = "uvicorn app.main:app --host 0.0.0.0 --port 8000 & nginx -g 'daemon off;' --no-daemon"
        files = {"Dockerfile": "FROM python:3.11-slim\nEXPOSE 8080\nCMD " + json.dumps(["/bin/sh", "-c", command])}
        corrected = CoderAgent._validate_deployment_contract(files)
        args = json.loads(corrected["Dockerfile"].split("CMD ")[1])
        self.assertEqual(args[2], "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 & nginx -g 'daemon off;'")
        self.assertEqual(normalize_startup(corrected), corrected)
        self.assertIn("--no-daemon", files["Dockerfile"])

    def test_exec_and_direct_command_forms(self):
        for original, expected in [
            ('CMD ["uvicorn", "app.main:app"]', 'CMD ["python", "-m", "uvicorn", "app.main:app"]'),
            ('CMD exec uvicorn app.main:app', 'CMD exec python -m uvicorn app.main:app'),
        ]:
            fixed = normalize_startup({"Dockerfile": "FROM python:3.11\n" + original})
            self.assertIn(expected, fixed["Dockerfile"])

    def test_other_runtimes_and_command_data_are_preserved(self):
        for dockerfile in [
            'FROM custom-runtime\nCMD ["uvicorn", "main:app"]',
            'FROM python:3.11\nCMD echo uvicorn app.main:app',
            'FROM node:22\nCMD ["npm", "start"]',
        ]:
            self.assertEqual(normalize_startup({"Dockerfile": dockerfile})["Dockerfile"], dockerfile)

    def test_emailstr_runtime_dependency_is_added_once(self):
        files = {"backend/app/main.py": "from pydantic import BaseModel, EmailStr\n", "backend/requirements.txt": "fastapi\nuvicorn\npydantic\n"}
        fixed = normalize_startup(files)
        self.assertIn("\nemail-validator\n", fixed["backend/requirements.txt"])
        self.assertEqual(normalize_startup(fixed), fixed)
        files["backend/requirements.txt"] += "pydantic[email]\n"
        self.assertEqual(normalize_startup(files), files)


if __name__ == "__main__":
    unittest.main()
