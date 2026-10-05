import json
import unittest

from app.agents.coder_agent import CoderAgent
from app.agents.container_startup import normalize_startup


class ContainerStartupTests(unittest.TestCase):
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
