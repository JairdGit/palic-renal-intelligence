import unittest
import pandas as pd
from src.data_quality.validation import validate_datasets


class RelationalIdentityValidationV084(unittest.TestCase):
    def setUp(self):
        self.p = pd.DataFrame([
            {"patient_id": "SYN-001", "age_years": 50, "sex": "F", "region": "X", "scenario": "stable"},
            {"patient_id": "SYN-002", "age_years": 61, "sex": "M", "region": "X", "scenario": "variable"},
        ])
        self.r = pd.DataFrame([
            {"patient_id": "SYN-001", "measurement_date": "2024-01-01", "egfr_ml_min_1_73m2": 90, "creatinine_mg_dl": 1.0, "measurement_sequence": 1},
            {"patient_id": "SYN-001", "measurement_date": "2024-03-01", "egfr_ml_min_1_73m2": 88, "creatinine_mg_dl": 1.1, "measurement_sequence": 2},
            {"patient_id": "SYN-002", "measurement_date": "2024-01-05", "egfr_ml_min_1_73m2": 82, "creatinine_mg_dl": 1.2, "measurement_sequence": 1},
        ])
        self.c = pd.DataFrame([
            {"patient_id": "SYN-001", "hypertension_simulated": 0, "diabetes_simulated": 0, "bmi_simulated": 24},
            {"patient_id": "SYN-002", "hypertension_simulated": 1, "diabetes_simulated": 0, "bmi_simulated": 27},
        ])

    def check(self, name):
        report = validate_datasets(self.p, self.r, self.c)
        return next(x for x in report["checks"] if x["check"] == name)

    def test_baseline_relational_contract_passes(self):
        report = validate_datasets(self.p, self.r, self.c)
        for name in ("patient_identifier_integrity", "renal_foreign_key_integrity",
                     "clinical_foreign_key_integrity", "clinical_patient_coverage", "renal_patient_coverage"):
            self.assertTrue(next(x for x in report["checks"] if x["check"] == name)["passed"], name)

    def test_null_renal_foreign_key_fails(self):
        self.r.loc[0, "patient_id"] = None
        self.assertFalse(self.check("renal_foreign_key_integrity")["passed"])

    def test_blank_clinical_foreign_key_fails(self):
        self.c.loc[0, "patient_id"] = "   "
        self.assertFalse(self.check("patient_identifier_integrity")["passed"])

    def test_orphan_clinical_patient_fails(self):
        self.c.loc[1, "patient_id"] = "SYN-999"
        self.assertFalse(self.check("clinical_foreign_key_integrity")["passed"])

    def test_missing_clinical_patient_coverage_fails(self):
        self.c = self.c.iloc[:1].copy()
        self.assertFalse(self.check("clinical_patient_coverage")["passed"])

    def test_missing_renal_patient_coverage_fails(self):
        self.r = self.r[self.r.patient_id != "SYN-002"].copy()
        self.assertFalse(self.check("renal_patient_coverage")["passed"])

    def test_whitespace_padded_identifier_fails_without_rewriting(self):
        original = self.r.loc[0, "patient_id"]
        self.r.loc[0, "patient_id"] = " SYN-001 "
        self.assertFalse(self.check("patient_identifier_integrity")["passed"])
        self.assertEqual(self.r.loc[0, "patient_id"], " SYN-001 ")
        self.assertNotEqual(original, self.r.loc[0, "patient_id"])

    def test_casefold_collision_in_patient_master_fails(self):
        self.p.loc[1, "patient_id"] = "syn-001"
        self.assertFalse(self.check("patient_identifier_integrity")["passed"])

    def test_normalized_reference_detects_case_mismatch(self):
        self.r.loc[0, "patient_id"] = "syn-001"
        self.assertFalse(self.check("renal_foreign_key_integrity")["passed"])
        # Foreign keys must match the master identifier exactly; normalization
        # is diagnostic only and never silently rewrites identity.


if __name__ == "__main__":
    unittest.main()
