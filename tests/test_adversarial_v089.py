"""Adversarial tests for v0.8.9 runtime preflight ordering and release readiness."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.environment.check import check_environment, EnvironmentCheckError, _read_requirements

ROOT = Path(__file__).resolve().parents[1]


class RuntimePreflightV089(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "requirements.txt").write_text(
            "packaging>=23,<27\npandas>=2.2,<4\nnumpy>=1.26,<3\n"
            "scikit-learn==1.9.0\njoblib==1.5.3\nstreamlit>=1.40,<2\nplotly>=5.20,<7\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_app_profile_fails_closed_for_missing_and_mismatched_packages(self):
        result = check_environment(
            self.root, profile="app", python_version="3.13.5",
            installed_versions={"packaging":"25.0", "pandas":"2.2.3", "numpy":"2.3.5",
                                "scikit-learn":"1.8.0", "joblib":"1.5.3", "plotly":"6.5.2"},
        )
        self.assertFalse(result["all_checks_passed"])
        failed = {item["name"]: item for item in result["failures"]}
        self.assertIn("scikit-learn", failed)
        self.assertIn("streamlit", failed)

    def test_core_profile_is_independent_of_ui_dependencies(self):
        result = check_environment(
            self.root, profile="core", python_version="3.13.5",
            installed_versions={"pandas":"2.2.3", "numpy":"2.3.5"},
        )
        self.assertTrue(result["all_checks_passed"])
        self.assertEqual({item["name"] for item in result["dependency_checks"]}, {"pandas", "numpy"})

    def test_requirements_reject_nested_includes_and_editable_installs(self):
        for line in ("-r other.txt", "-e .", "--index-url https://example.invalid"):
            path = self.root / "bad.txt"
            path.write_text(line + "\n", encoding="utf-8")
            with self.subTest(line=line), self.assertRaises(EnvironmentCheckError):
                _read_requirements(path)

    def test_python_invalid_version_is_not_reported_as_compatible(self):
        with self.assertRaises(Exception):
            check_environment(self.root, profile="core", python_version="not-a-version",
                              installed_versions={"pandas":"2.2.3", "numpy":"2.3.5"})

    def test_app_preflight_occurs_before_streamlit_import(self):
        bootstrap = (
            "import importlib.metadata as md, runpy, sys; "
            "original = md.version; "
            "md.version = lambda name: (_ for _ in ()).throw(md.PackageNotFoundError(name)) "
            "if name.lower() == 'streamlit' else original(name); "
            "runpy.run_path(sys.argv[1], run_name='__main__')"
        )
        result = subprocess.run(
            [sys.executable, "-c", bootstrap, str(ROOT / "app.py")],
            cwd=ROOT, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Entorno incompatible", result.stderr)
        self.assertNotIn("No module named 'streamlit'", result.stderr)

    def test_app_imports_are_textually_after_preflight_guard(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        guard = source.index('if not ENVIRONMENT["all_checks_passed"]:')
        streamlit_import = source.index("import streamlit as st")
        self.assertLess(guard, streamlit_import)

    def test_manifest_declares_correct_release_version(self):
        manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertFalse(manifest["predictive_model_connected"])
        self.assertEqual(manifest["data_policy"], "SYNTHETIC_ONLY")


if __name__ == "__main__":
    unittest.main()
