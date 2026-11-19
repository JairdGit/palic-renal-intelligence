from __future__ import annotations
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.dashboard.demo_exports import csv_export_with_provenance
from src.environment.check import check_environment
from src.integrity.manifest import verify_release_manifest
from src.io_safety.safe_io import ArtifactReadError, read_csv_checked
from src.synthetic_data.generator import generate_synthetic_data
from src.longitudinal_engine.engine import build_longitudinal_dataset
from src.model_integration.contract import load_predictor_contract

ROOT = Path(__file__).resolve().parents[1]


def write_manifest(root: Path, files: dict[str, str], version="1.0.0"):
    (root / "RELEASE_MANIFEST.json").write_text(json.dumps({"version": version, "file_sha256": files}), encoding="utf-8")


class Audit01FunctionalArchitecture(unittest.TestCase):
    def test_demo_generator_reproducible_for_seed(self):
        a = generate_synthetic_data(25, 1234)
        b = generate_synthetic_data(25, 1234)
        for left, right in zip(a, b):
            pd.testing.assert_frame_equal(left, right)

    def test_generator_rejects_fractional_patient_count(self):
        with self.assertRaises(ValueError):
            generate_synthetic_data(10.5, 1)

    def test_generator_rejects_boolean_seed(self):
        with self.assertRaises(ValueError):
            generate_synthetic_data(10, True)


class Audit02ScientificOutcome(unittest.TestCase):
    def test_censored_outcomes_remain_null(self):
        _, renal, _ = generate_synthetic_data(50, 20261105)
        landmarks, _ = build_longitudinal_dataset(renal)
        censored = landmarks.loc[landmarks.evaluable_365.eq(0), "target_sustained_40"]
        self.assertTrue(censored.isna().all())

    def test_event_definition_and_model_boundary_are_explicit(self):
        engine = (ROOT / "src/longitudinal_engine/engine.py").read_text(encoding="utf-8")
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn(">=30", engine)
        self.assertIn("365", engine)
        self.assertIn("Modelo predictivo real no conectado", app)


class Audit03TemporalIntegrity(unittest.TestCase):
    def test_generated_dates_are_valid_and_sorted_by_patient(self):
        _, renal, _ = generate_synthetic_data(50, 20261105)
        dates = pd.to_datetime(renal.measurement_date, errors="coerce")
        self.assertFalse(dates.isna().any())
        work = renal.assign(_date=dates)
        for _, group in work.groupby("patient_id"):
            self.assertTrue(group._date.is_monotonic_increasing)

    def test_measurement_sequence_is_integer_positive(self):
        _, renal, _ = generate_synthetic_data(50, 20261105)
        seq = pd.to_numeric(renal.measurement_sequence, errors="coerce")
        self.assertTrue(seq.notna().all())
        self.assertTrue((seq > 0).all())
        self.assertTrue((seq % 1 == 0).all())


class Audit04RelationalDataQuality(unittest.TestCase):
    def test_generated_tables_have_synthetic_ids_and_matching_master(self):
        patients, renal, clinical = generate_synthetic_data(50, 20261105)
        master = set(patients.patient_id)
        self.assertEqual(len(master), 50)
        self.assertTrue(all(str(x).startswith("SYN-") for x in master))
        self.assertEqual(set(clinical.patient_id), master)
        self.assertLessEqual(set(renal.patient_id), master)

    def test_clinical_and_patient_master_ids_are_unique(self):
        patients, _, clinical = generate_synthetic_data(50, 20261105)
        self.assertTrue(patients.patient_id.is_unique)
        self.assertTrue(clinical.patient_id.is_unique)


class Audit05ManifestAndSupplyChain(unittest.TestCase):
    def test_strict_manifest_rejects_unlisted_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "known.txt").write_text("known", encoding="utf-8")
            digest = hashlib.sha256(b"known").hexdigest()
            write_manifest(root, {"known.txt": digest})
            (root / "unlisted.py").write_text("# tampered addition", encoding="utf-8")
            result = verify_release_manifest(root, strict=True, expected_version="1.0.0")
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("unlisted.py", result["unlisted"])

    def test_strict_manifest_ignores_git_metadata_and_streamlit_runtime_secrets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "known.txt").write_text("known", encoding="utf-8")
            digest = hashlib.sha256(b"known").hexdigest()
            write_manifest(root, {"known.txt": digest})
            (root / ".git" / "objects").mkdir(parents=True)
            (root / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
            (root / ".streamlit").mkdir()
            (root / ".streamlit" / "secrets.toml").write_text("token='runtime-only'", encoding="utf-8")
            result = verify_release_manifest(root, strict=True, expected_version="1.0.0")
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["unlisted"], [])

    def test_strict_manifest_still_rejects_unlisted_streamlit_config(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "known.txt").write_text("known", encoding="utf-8")
            write_manifest(root, {"known.txt": hashlib.sha256(b"known").hexdigest()})
            (root / ".streamlit").mkdir()
            (root / ".streamlit" / "config.toml").write_text("[theme]", encoding="utf-8")
            result = verify_release_manifest(root, strict=True, expected_version="1.0.0")
            self.assertEqual(result["status"], "FAIL")
            self.assertIn(".streamlit/config.toml", result["unlisted"])

    def test_strict_manifest_rejects_wrong_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "known.txt").write_text("known", encoding="utf-8")
            write_manifest(root, {"known.txt": hashlib.sha256(b"known").hexdigest()}, "0.9.9")
            result = verify_release_manifest(root, strict=True, expected_version="1.0.0")
            self.assertEqual(result["status"], "VERSION_MISMATCH")

    def test_strict_manifest_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            outside = root.parent / (root.name + "_outside.txt")
            outside.write_text("outside", encoding="utf-8")
            try:
                (root / "link.txt").symlink_to(outside)
                write_manifest(root, {"link.txt": hashlib.sha256(b"outside").hexdigest()})
                result = verify_release_manifest(root, strict=True)
                self.assertEqual(result["status"], "FAIL")
            finally:
                outside.unlink(missing_ok=True)


class Audit06InputOutputSecurity(unittest.TestCase):
    def test_duplicate_csv_headers_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.csv"
            path.write_text("patient_id,patient_id\nSYN-1,SYN-2\n", encoding="utf-8")
            with self.assertRaises(ArtifactReadError):
                read_csv_checked(path, required_columns=["patient_id"])

    def test_formula_injection_is_neutralized_in_text_columns(self):
        frame = pd.DataFrame({"label": ["=1+1", "  @SUM(A1:A2)", "normal"], "value": [-2, 3, 4]})
        content = csv_export_with_provenance(frame, "1.0.0", "adversarial_test").decode("utf-8-sig")
        self.assertIn("'=1+1", content)
        self.assertIn("'  @SUM(A1:A2)", content)
        self.assertIn("-2", content)


class Audit07ModelBoundary(unittest.TestCase):
    def test_predictor_contract_remains_28_and_ordered(self):
        contract = load_predictor_contract(ROOT / "models/research_reference/effective_predictors.json", family="full_clinical")
        self.assertEqual(len(contract), 28)
        self.assertEqual(len(set(contract)), 28)

    def test_app_does_not_enable_model_inference(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("Modelo predictivo real no conectado", app)
        self.assertNotIn("predict_patient(", app)


class Audit08DashboardAndUsability(unittest.TestCase):
    def test_six_dashboard_pages_exist(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        for page in ("Resumen", "Trayectorias", "Auditoría por paciente", "Inteligencia de riesgo", "Calidad de datos", "Trazabilidad"):
            self.assertIn(page, app)

    def test_streamlit_is_declared_but_visual_test_is_not_falsely_claimed(self):
        req = (ROOT / "requirements-app.txt").read_text(encoding="utf-8")
        report = (ROOT / "TEN_ADVERSARIAL_AUDITS.md").read_text(encoding="utf-8")
        self.assertIn("streamlit", req.lower())
        self.assertIn("BLOQUEADA", report)
        self.assertIn("Streamlit", report)


class Audit09ReproducibilityAndDependencies(unittest.TestCase):
    def test_core_profile_passes_current_environment(self):
        result = check_environment(ROOT, profile="core")
        self.assertTrue(result["all_checks_passed"])

    def test_app_and_model_profiles_are_reported_without_claiming_pass(self):
        app = check_environment(ROOT, profile="app")
        model = check_environment(ROOT, profile="model")
        self.assertEqual(app["profile"], "app")
        self.assertEqual(model["profile"], "model")
        self.assertIsInstance(app["all_checks_passed"], bool)
        self.assertIsInstance(model["all_checks_passed"], bool)


class Audit10SubmissionAndDocumentation(unittest.TestCase):
    def test_release_docs_identify_synthetic_only_and_no_clinical_use(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("synthetic", readme)
        self.assertIn("no es un dispositivo médico", readme)
        self.assertIn("modelo predictivo real no conectado", readme)

    def test_pitch_deck_and_demo_video_not_fabricated_as_included(self):
        report = (ROOT / "TEN_ADVERSARIAL_AUDITS.md").read_text(encoding="utf-8")
        self.assertIn("plantilla oficial del pitch deck", report.lower())
        self.assertIn("video público", report.lower())
        self.assertIn("no están incluidos", report.lower())


if __name__ == "__main__":
    unittest.main()
