import unittest

from app.agents.poetry_packaging import resolve_poetry_before_install
from app.agents.deployment_contract import poetry_project_issues
from app.agents.coder_agent import CoderAgent


class PoetryPackaging(unittest.TestCase):
    def test_selected_toolchain_resolves_lock_before_install_preserving_flags(self):
        source = 'FROM python:3.12\nRUN pip install poetry==2.2.1\nRUN poetry config virtualenvs.create false \\\n    && poetry install --only main --no-root\n'
        result = resolve_poetry_before_install(source)
        self.assertIn('pip install poetry==2.2.1', result)
        self.assertIn('rm -f poetry.lock && poetry lock --no-interaction && poetry install --only main --no-root', result)
        self.assertEqual(resolve_poetry_before_install(result), result)

    def test_resolution_failure_cannot_fall_through_to_install(self):
        result = resolve_poetry_before_install('RUN poetry install\n')
        self.assertIn('poetry lock --no-interaction && poetry install', result)
        self.assertNotIn('||', result)

    def test_json_and_python_module_commands(self):
        for source in ('RUN ["poetry", "install", "--no-root"]\n',
                       'RUN ["/bin/sh", "-c", "poetry install --no-root"]\n',
                       'RUN python -m poetry install --no-root\n'):
            result = resolve_poetry_before_install(source)
            self.assertIn('lock --no-interaction', result)
            self.assertEqual(resolve_poetry_before_install(result), result)

    def test_other_stacks_strings_and_custom_shell_programs_remain_unchanged(self):
        for source in ('RUN pip install -r requirements.txt\n', 'RUN npm ci\n',
                       'RUN echo "poetry install"\n', 'RUN echo "x && poetry install"\n',
                       'RUN if test -f poetry.lock; then poetry install; fi\n',
                       'RUN <<EOF\npoetry install\nEOF\n'):
            self.assertEqual(resolve_poetry_before_install(source), source)

    def fixture(self, config=''):
        return {'Dockerfile': 'FROM python:3.11\nCOPY backend/ /app\nRUN poetry install\nEXPOSE 8080\n',
                'backend/pyproject.toml': '[tool.poetry]\nname="generated-service"\nversion="0.1.0"\n' + config,
                'backend/app/main.py': 'app = None\n'}

    def test_uninstallable_application_package_is_returned_to_coder(self):
        with self.assertRaisesRegex(ValueError, 'no matching root package'):
            CoderAgent._validate_deployment_contract(self.fixture())

    def test_nonpackage_app_and_real_package_layout_are_supported(self):
        self.assertEqual(poetry_project_issues(self.fixture('package-mode=false\n')), [])
        files = self.fixture()
        files['backend/src/generated_service/__init__.py'] = ''
        self.assertEqual(poetry_project_issues(files), [])
        files = self.fixture('packages=[{include="app"}]\n')
        self.assertEqual(poetry_project_issues(files), [])
        files = self.fixture()
        files['Dockerfile'] = files['Dockerfile'].replace('poetry install', 'poetry install --no-root')
        self.assertEqual(poetry_project_issues(files), [])
