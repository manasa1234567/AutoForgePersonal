import unittest
from app.agents.frontend_contract import expects_browser_ui, frontend_issues
from app.agents.coder_agent import CoderAgent


class FrontendContract(unittest.TestCase):
    def test_approved_react_cannot_be_backend_only(self):
        files = {'Dockerfile': 'FROM python:3.11\nCOPY app app\nEXPOSE 8080\n',
                 'app/main.py': 'message = "Backend is running"'}
        with self.assertRaisesRegex(ValueError, 'no browser UI source'):
            CoderAgent._validate_deployment_contract(files, 'Recommended: React web application')

    def test_api_only_project_remains_supported(self):
        for name in ('None', 'No frontend', 'API-only', 'Recommended: None'):
            self.assertFalse(expects_browser_ui(name))
            self.assertEqual(frontend_issues({'app.py':'app = None'}, name), [])

    def test_browser_source_for_multiple_stacks(self):
        for frontend, file in [('React', 'frontend/src/App.tsx'), ('Angular', 'src/app/app.html'),
                               ('Vue', 'web/App.vue'), ('Svelte', 'src/App.svelte'),
                               ('Blazor', 'Pages/Home.razor')]:
            self.assertEqual(frontend_issues({file:'source'}, frontend), [])

    def test_test_files_do_not_satisfy_ui_requirement(self):
        files = {'tests/fixture.html':'test', 'frontend/src/App.test.tsx':'test'}
        self.assertTrue(frontend_issues(files, 'React'))

    def test_compiled_javascript_source_layout(self):
        self.assertEqual(frontend_issues({'frontend/src/App.js':'source'}, 'React'), [])
