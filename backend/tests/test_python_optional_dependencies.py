import unittest

from app.agents.python_optional_dependencies import optional_dependency_issues, uses_pydantic_email
from app.agents.coder_agent import CoderAgent
from app.agents.critic_agent import CriticAgent


class PythonOptionalDependencies(unittest.TestCase):
    def poetry(self, email='^1.3.1', pydantic='2.11.3'):
        return {'Dockerfile': 'FROM python:3.11\nCOPY app ./app\nCOPY pyproject.toml ./\nRUN poetry install --no-root\nEXPOSE 8080\n',
                'pyproject.toml': f'[tool.poetry]\nname="service"\nversion="0.1.0"\npackage-mode=false\n[tool.poetry.dependencies]\npydantic="{pydantic}"\nemail-validator="{email}"\n',
                'app/models.py': 'from pydantic import BaseModel, EmailStr\nclass User(BaseModel):\n    email: EmailStr\n'}

    def test_poetry_incompatibility_blocks_coder_and_critic(self):
        files = self.poetry()
        with self.assertRaisesRegex(ValueError, 'email-validator>=2.0'):
            CoderAgent._validate_deployment_contract(files)
        findings, checks = CriticAgent()._local_checks(files)
        self.assertEqual(checks['deployment_contract'], 'Failed')
        self.assertTrue(any('email-validator>=2.0' in finding.issue for finding in findings))
        self.assertTrue(optional_dependency_issues(self.poetry('~1.3.1')))

    def test_compatible_versions_and_unused_email_dependencies_are_preserved(self):
        for version in ('^2.0', '>=2.0', '2.2.0', '>=1.3,<3', '<2.1'):
            files = self.poetry(version)
            before = dict(files)
            self.assertEqual(optional_dependency_issues(files), [])
            self.assertEqual(files, before)
        files = self.poetry(pydantic='1.10.26')
        self.assertEqual(optional_dependency_issues(files), [])
        files = self.poetry()
        files['app/models.py'] = 'from pydantic import BaseModel\n'
        self.assertEqual(optional_dependency_issues(files), [])

    def test_requirements_and_pep621_reject_old_email_version(self):
        source = {'src/user.py': 'import pydantic as p\nclass User(p.BaseModel):\n    email: p.EmailStr\n'}
        for manifest, contents in (
            ('requirements.txt', 'pydantic==2.11.3\nemail-validator==1.3.1\n'),
            ('requirements.txt', 'pydantic>=2.0\nemail-validator>=1.3,<2\n'),
            ('pyproject.toml', '[project]\nname="service"\ndependencies=["pydantic==2.11.3", "email-validator<2"]\n'),
        ):
            self.assertTrue(optional_dependency_issues({**source, manifest: contents}))

    def test_optional_extras_satisfy_missing_distribution_and_dev_only_does_not(self):
        source = {'app/models.py': 'from pydantic import NameEmail\n'}
        for contents in (
            '[project]\ndependencies=["pydantic[email]==2.11.3"]\n',
            '[tool.poetry.dependencies]\npydantic={version="2.11.3",extras=["email"]}\n',
            '[tool.poetry.dependencies]\nfastapi={version="0.115.12",extras=["standard"]}\n',
        ):
            self.assertEqual(optional_dependency_issues({**source, 'pyproject.toml': contents}), [])
        contents = '[tool.poetry.dependencies]\npydantic="2.11.3"\n[tool.poetry.group.dev.dependencies]\nemail-validator="^2"\n'
        self.assertTrue(optional_dependency_issues({**source, 'pyproject.toml': contents}))

    def test_import_aliases_multiline_and_unrelated_names(self):
        for source in ('from pydantic import (\n BaseModel,\n EmailStr as Address,\n)\n',
                       'from pydantic.networks import NameEmail\n',
                       'import pydantic as p\nemail: p.EmailStr\n'):
            self.assertTrue(uses_pydantic_email(source))
        self.assertFalse(uses_pydantic_email('from another_library import EmailStr\n'))
        self.assertFalse(uses_pydantic_email('email = "EmailStr"\n'))

    def test_test_fixtures_do_not_require_runtime_extra(self):
        self.assertEqual(optional_dependency_issues({'pyproject.toml': '[tool.poetry.dependencies]\npydantic="2.11.3"',
                                                    'tests/test_user.py': 'from pydantic import EmailStr'}), [])

    def test_duplicate_and_normalized_distribution_names_do_not_hide_old_constraint(self):
        files = {'app/user.py': 'from pydantic import EmailStr\n',
                 'requirements.txt': 'pydantic==2.11.3\npydantic[email]\nemail.validator==1.3.1\nemail-validator\n'}
        self.assertTrue(optional_dependency_issues(files))

    def test_requirements_subdirectory_scopes_application_sources(self):
        files = {'backend/requirements/runtime.txt': 'pydantic==2.11.3\nemail-validator==1.3.1\n',
                 'backend/app/user.py': 'from pydantic import EmailStr\n'}
        self.assertTrue(optional_dependency_issues(files))

    def test_star_import_and_malformed_extras(self):
        self.assertTrue(uses_pydantic_email('from pydantic import *\nclass User(BaseModel):\n    email: EmailStr\n'))
        files = {'pyproject.toml': '[tool.poetry.dependencies]\npydantic={version="2.11.3",extras=4}\n',
                 'app/user.py': 'from pydantic import EmailStr\n'}
        self.assertTrue(optional_dependency_issues(files))
