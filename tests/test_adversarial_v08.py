import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd
from src.data_quality.validation import validate_datasets
from src.synthetic_data.generator import generate_synthetic_data
from src.integrity.manifest import verify_release_manifest

class DataQualityAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.p, self.r, self.c = generate_synthetic_data(40, 20261105)

    def test_baseline_synthetic_data_passes_expanded_contract(self):
        report = validate_datasets(self.p, self.r, self.c)
        self.assertTrue(report["all_checks_passed"])
        self.assertEqual(report["checks_total"], 27)

    def test_orphan_renal_patient_is_detected(self):
        bad = self.r.copy()
        bad.loc[bad.index[0], "patient_id"] = "SYN-ORPHAN"
        report = validate_datasets(self.p, bad, self.c)
        check = next(x for x in report["checks"] if x["check"] == "renal_patient_references")
        self.assertFalse(check["passed"])

    def test_duplicate_clinical_patient_is_detected(self):
        bad = pd.concat([self.c, self.c.iloc[[0]]], ignore_index=True)
        report = validate_datasets(self.p, self.r, bad)
        check = next(x for x in report["checks"] if x["check"] == "unique_clinical_patient_rows")
        self.assertFalse(check["passed"])

    def test_invalid_creatinine_is_detected(self):
        bad = self.r.copy()
        bad.loc[bad.index[0], "creatinine_mg_dl"] = 0
        report = validate_datasets(self.p, bad, self.c)
        check = next(x for x in report["checks"] if x["check"] == "positive_creatinine")
        self.assertFalse(check["passed"])

    def test_non_synthetic_identifier_is_detected(self):
        bad = self.p.copy()
        bad.loc[bad.index[0], "patient_id"] = "PATIENT-001"
        report = validate_datasets(bad, self.r, self.c)
        check = next(x for x in report["checks"] if x["check"] == "synthetic_identifier_prefix")
        self.assertFalse(check["passed"])

class ManifestIntegrityTests(unittest.TestCase):
    def test_manifest_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.txt").write_text("original", encoding="utf-8")
            import hashlib
            digest = hashlib.sha256(b"original").hexdigest()
            (root / "RELEASE_MANIFEST.json").write_text(json.dumps({
                "version":"0.8", "file_sha256":{"sample.txt":digest}
            }), encoding="utf-8")
            self.assertEqual(verify_release_manifest(root)["status"], "PASS")
            (root / "sample.txt").write_text("tampered", encoding="utf-8")
            result = verify_release_manifest(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["failed"], ["sample.txt"])

    def test_missing_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(verify_release_manifest(tmp)["status"], "MISSING_MANIFEST")

if __name__ == "__main__":
    unittest.main()


class LongitudinalContractAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.p, self.r, self.c = generate_synthetic_data(40, 20261105)

    def _check(self, renal, name):
        report = validate_datasets(self.p, renal, self.c)
        return next(item for item in report["checks"] if item["check"] == name)

    def test_duplicate_sequence_for_same_patient_fails(self):
        bad = self.r.copy()
        idx = bad.index[1]
        bad.loc[idx, "measurement_sequence"] = bad.loc[bad.index[0], "measurement_sequence"]
        self.assertFalse(self._check(bad, "unique_sequence_per_patient")["passed"])

    def test_sequence_reversal_against_dates_fails(self):
        bad = self.r.copy()
        patient = bad.loc[0, "patient_id"]
        indices = bad.index[bad.patient_id == patient][:2]
        bad.loc[indices[0], "measurement_sequence"] = 2
        bad.loc[indices[1], "measurement_sequence"] = 1
        self.assertFalse(self._check(bad, "sequence_matches_chronology")["passed"])

    def test_sequence_gap_fails(self):
        bad = self.r.copy()
        bad.loc[bad.index[1], "measurement_sequence"] = 4
        self.assertFalse(self._check(bad, "contiguous_patient_sequence")["passed"])

    def test_fractional_sequence_fails(self):
        bad = self.r.copy()
        bad["measurement_sequence"] = bad["measurement_sequence"].astype(float)
        bad.loc[bad.index[0], "measurement_sequence"] = 1.5
        self.assertFalse(self._check(bad, "valid_measurement_sequence")["passed"])

    def test_negative_sequence_fails(self):
        bad = self.r.copy()
        bad.loc[bad.index[0], "measurement_sequence"] = -1
        self.assertFalse(self._check(bad, "valid_measurement_sequence")["passed"])

    def test_baseline_sequence_contract_passes(self):
        for name in ("unique_sequence_per_patient", "sequence_matches_chronology", "contiguous_patient_sequence"):
            self.assertTrue(self._check(self.r, name)["passed"], name)
