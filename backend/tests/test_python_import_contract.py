import unittest
from app.agents.python_import_contract import local_import_issues
from app.agents.deployment_contract import packaging_issues


class LocalImports(unittest.TestCase):
    def test_missing_symbol_in_nested_backend_is_reported(self):
        files = {'backend/app/routes.py': 'from app.services.sessions import create_session\n',
                 'backend/app/services/sessions.py': 'async def list_sessions():\n    return []\n'}
        issues = packaging_issues(files)
        self.assertEqual(len(issues), 1)
        self.assertIn('create_session', issues[0])
        self.assertIn('backend/app/services/sessions.py', issues[0])
        files['backend/app/services/sessions.py'] += '\nasync def create_session():\n    return {}\n'
        self.assertEqual(local_import_issues(files), [])

    def test_aliases_relative_imports_and_submodules(self):
        files = {'app/routes.py': 'from .services import create_session as create\nfrom app import helpers\n',
                 'app/services.py': 'from external import create_session\n',
                 'app/__init__.py': '', 'app/helpers.py': ''}
        self.assertEqual(local_import_issues(files), [])

    def test_dynamic_external_and_optional_imports_not_rejected(self):
        files = {'app/main.py': 'from external import missing\nfrom app.dynamic import value\ntry:\n    from app.empty import optional\nexcept ImportError:\n    optional = None\n',
                 'app/dynamic.py': 'def __getattr__(name):\n    return 1\n', 'app/empty.py': ''}
        self.assertEqual(local_import_issues(files), [])

    def test_ambiguous_source_roots_not_guessed(self):
        files = {'main.py': 'from app.service import thing\n',
                 'first/app/service.py': '', 'second/app/service.py': 'thing = 1'}
        self.assertEqual(local_import_issues(files), [])

    def test_all_missing_symbols_reported_together(self):
        files = {'app/api.py': 'from app.service import one, two\n', 'app/service.py': ''}
        self.assertEqual(len(local_import_issues(files)), 2)
