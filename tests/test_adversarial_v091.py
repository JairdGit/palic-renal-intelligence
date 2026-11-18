"""Adversarial tests for v0.9.1 dependency separation and dashboard readiness."""
import ast
import json
import tempfile
import unittest
from pathlib import Path

from src.environment.check import check_environment

ROOT = Path(__file__).resolve().parents[1]


class DependencySeparationV091(unittest.TestCase):
    def test_dashboard_requirements_do_not_include_model_training_stack(self):
        text = (ROOT / "requirements-app.txt").read_text(encoding="utf-8")
        names = {line.split("=")[0].split(">=")[0].split("<")[0].strip().lower()
                 for line in text.splitlines() if line.strip() and not line.startswith("#")}
        self.assertNotIn("scikit-learn", names)

    def test_model_requirements_preserve_exact_research_versions(self):
        text = (ROOT / "requirements-model.txt").read_text(encoding="utf-8")
        self.assertIn("scikit-learn==1.9.0", text)
        self.assertIn("joblib==1.5.3", text)

    def test_app_profile_uses_app_requirements_file(self):
        result = check_environment(ROOT, profile="app", python_version="3.13.5",
                                   installed_versions={"packaging":"25.0", "pandas":"2.2.3",
                                                       "numpy":"2.3.5", "joblib":"1.5.3",
                                                       "plotly":"6.5.2", "streamlit":"1.50.0"})
        names = {item["name"] for item in result["dependency_checks"]}
        self.assertNotIn("scikit-learn", names)
        self.assertIn("streamlit", names)
        self.assertTrue(result["all_checks_passed"])

    def test_model_profile_checks_model_requirements(self):
        result = check_environment(ROOT, profile="model", python_version="3.13.5",
                                   installed_versions={"scikit-learn":"1.9.0", "joblib":"1.5.3"})
        self.assertEqual({x["name"] for x in result["dependency_checks"]}, {"scikit-learn", "joblib"})
        self.assertTrue(result["all_checks_passed"])

    def test_app_profile_still_fails_closed_when_streamlit_is_missing(self):
        result = check_environment(ROOT, profile="app", python_version="3.13.5",
                                   installed_versions={"packaging":"25.0", "pandas":"2.2.3",
                                                       "numpy":"2.3.5", "joblib":"1.5.3",
                                                       "plotly":"6.5.2"})
        self.assertFalse(result["all_checks_passed"])
        self.assertEqual([x["name"] for x in result["failures"]], ["streamlit"])

    def test_dashboard_navigation_has_six_expected_sections(self):
        tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        expected = ["Resumen", "Trayectorias", "Auditoría por paciente",
                    "Inteligencia de riesgo", "Calidad de datos", "Trazabilidad"]
        for section in expected:
            with self.subTest(section=section):
                self.assertIn(section, source)
        self.assertIsInstance(tree, ast.Module)

    def test_dashboard_still_declares_synthetic_only_and_model_disconnected(self):
        manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["data_policy"], "SYNTHETIC_ONLY")
        self.assertFalse(manifest["predictive_model_connected"])
        self.assertEqual(manifest["predictor_contract_count"], 28)

    def test_generator_version_is_incremented(self):
        source = (ROOT / "run_demo.py").read_text(encoding="utf-8")
        self.assertIn("generator_version'] = 'v1.0.0'", source)


if __name__ == "__main__":
    unittest.main()
