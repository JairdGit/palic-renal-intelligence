from pathlib import Path
import tempfile
import unittest

from src.release.readiness import build_release_readiness

ROOT = Path(__file__).resolve().parents[1]


class TestReleaseReadinessV099(unittest.TestCase):
    def test_current_package_ready(self):
        result = build_release_readiness(ROOT)
        self.assertEqual(result["version"], "1.0.0")
        self.assertEqual(result["status"], "READY_FOR_FINAL_REVIEW")

    def test_six_checks_present(self):
        result = build_release_readiness(ROOT)
        self.assertEqual(result["checks_total"], 7)

    def test_all_checks_have_status(self):
        result = build_release_readiness(ROOT)
        self.assertTrue(all(item["status"] in {"PASS", "FAIL"} for item in result["checks"]))

    def test_missing_readme_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build_release_readiness(tmp)
        self.assertEqual(result["status"], "NOT_READY")

    def test_missing_historical_audits_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build_release_readiness(tmp)
        history = next(item for item in result["checks"] if item["name"] == "version_audit_history")
        self.assertEqual(history["status"], "FAIL")

    def test_scope_note_disclaims_clinical_validation(self):
        result = build_release_readiness(ROOT)
        self.assertIn("validación clínica", result["scope_note"])

    def test_package_hygiene_check_exists(self):
        result = build_release_readiness(ROOT)
        self.assertIn("package_hygiene", {item["name"] for item in result["checks"]})

    def test_dependency_profile_check_exists(self):
        result = build_release_readiness(ROOT)
        self.assertIn("dependency_profiles", {item["name"] for item in result["checks"]})

    def test_operator_documentation_check_exists(self):
        result = build_release_readiness(ROOT)
        self.assertIn("operator_documentation", {item["name"] for item in result["checks"]})

    def test_version_is_not_v1(self):
        result = build_release_readiness(ROOT)
        self.assertEqual(result["version"], "1.0.0")

    def test_status_is_not_full_release_certification(self):
        result = build_release_readiness(ROOT)
        self.assertEqual(result["status"], "READY_FOR_FINAL_REVIEW")
        self.assertIn("no ejecuta interfaz", result["scope_note"])

    def test_required_audit_history_count(self):
        result = build_release_readiness(ROOT)
        history = next(item for item in result["checks"] if item["name"] == "version_audit_history")
        self.assertEqual(history["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
