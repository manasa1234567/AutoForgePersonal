import unittest

from app.agents.critic_agent import CriticAgent
from app.agents.typescript_review import form_error_findings


BROKEN = '''interface FormData {
  name: string;
  acceptTerms: boolean;
  age: number;
}
const validate = () => {
  const newErrors: Partial<FormData> = {};
  if (!formData.acceptTerms) newErrors.acceptTerms = 'You must accept the terms';
  if (!formData.age) newErrors.age = 'Age required';
};
'''


class TypeScriptReviewTests(unittest.TestCase):
    def test_boolean_and_numeric_error_messages_are_diagnosed(self):
        findings = form_error_findings({"src/Form.tsx": BROKEN})
        self.assertEqual(len(findings), 2)
        self.assertTrue(all("TS2322" in f.issue for f in findings))
        self.assertTrue(all("Partial<Record<keyof FormData, string>>" in f.recommendation for f in findings))

    def test_string_error_map_keeps_original_form_types(self):
        fixed = BROKEN.replace("Partial<FormData>", "Partial<Record<keyof FormData, string>>")
        self.assertEqual(form_error_findings({"src/Form.tsx": fixed}), [])
        self.assertIn("acceptTerms: boolean", fixed)

    def test_comments_and_valid_boolean_assignments_are_ignored(self):
        source = BROKEN.replace("'You must accept the terms'", "true").replace("'Age required'", "18")
        source += "\n// newErrors.acceptTerms = 'message';\n/* newErrors.age = 'message'; */"
        self.assertEqual(form_error_findings({"src/Form.tsx": source}), [])

    def test_union_and_imported_types_are_left_to_compiler(self):
        source = BROKEN.replace("acceptTerms: boolean;", "acceptTerms: boolean | string;").replace("age: number;", "age: number | string;")
        self.assertEqual(form_error_findings({"src/Form.tsx": source}), [])

    def test_critic_marks_failed_check_to_trigger_existing_repair_loop(self):
        findings, checks = CriticAgent()._local_checks({
            "Dockerfile": "FROM node:22\nEXPOSE 8080\n",
            "src/Form.tsx": BROKEN,
        })
        self.assertEqual(checks["typescript_error_maps"], "Failed")
        self.assertTrue(any("TS2322" in f.issue for f in findings))


if __name__ == "__main__":
    unittest.main()
