import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.dashboard.validation import validate_dashboard_data, DashboardDataContractError


class DashboardContractV09Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = ROOT / "data" / "generated"
        cls.patients = pd.read_csv(d / "patients_synthetic.csv")
        cls.renal = pd.read_csv(d / "renal_measurements_synthetic.csv")
        cls.clinical = pd.read_csv(d / "clinical_variables_synthetic.csv")
        cls.landmarks = pd.read_csv(d / "longitudinal_landmarks_synthetic.csv")

    def copies(self):
        return [x.copy(deep=True) for x in (self.patients, self.renal, self.clinical, self.landmarks)]

    def test_generated_dashboard_data_contract_passes(self):
        report = validate_dashboard_data(*self.copies())
        self.assertTrue(report["all_checks_passed"])
        self.assertEqual(report["checks_passed"], report["checks_total"])

    def test_orphan_clinical_patient_fails(self):
        p, r, c, l = self.copies()
        c.loc[0, "patient_id"] = "SYN-NOT-FOUND"
        with self.assertRaises(DashboardDataContractError):
            validate_dashboard_data(p, r, c, l)

    def test_duplicate_master_patient_fails(self):
        p, r, c, l = self.copies()
        p.loc[1, "patient_id"] = p.loc[0, "patient_id"]
        with self.assertRaises(DashboardDataContractError):
            validate_dashboard_data(p, r, c, l)

    def test_duplicate_landmark_fails(self):
        p, r, c, l = self.copies()
        l.loc[1, "patient_id"] = l.loc[0, "patient_id"]
        with self.assertRaises(DashboardDataContractError):
            validate_dashboard_data(p, r, c, l)

    def test_non_synthetic_identifier_fails(self):
        p, r, c, l = self.copies()
        p.loc[0, "patient_id"] = "PATIENT-001"
        with self.assertRaises(DashboardDataContractError):
            validate_dashboard_data(p, r, c, l)

    def test_censored_target_must_remain_null(self):
        p, r, c, l = self.copies()
        idx = l.index[l["evaluable_365"] == 0][0]
        l.loc[idx, "target_sustained_40"] = 0
        with self.assertRaises(DashboardDataContractError):
            validate_dashboard_data(p, r, c, l)

    def test_evaluable_target_must_be_binary(self):
        p, r, c, l = self.copies()
        idx = l.index[l["evaluable_365"] == 1][0]
        l.loc[idx, "target_sustained_40"] = 2
        with self.assertRaises(DashboardDataContractError):
            validate_dashboard_data(p, r, c, l)

    def test_missing_required_column_fails_closed(self):
        p, r, c, l = self.copies()
        r.drop(columns=["egfr_ml_min_1_73m2"], inplace=True)
        with self.assertRaises(DashboardDataContractError):
            validate_dashboard_data(p, r, c, l)

    def test_renal_orphan_fails(self):
        p, r, c, l = self.copies()
        r.loc[0, "patient_id"] = "SYN-ORPHAN"
        with self.assertRaises(DashboardDataContractError):
            validate_dashboard_data(p, r, c, l)


    def test_dashboard_checks_manifest_before_loading_data(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertLess(source.index('INTEGRITY = verify_release_manifest(ROOT, strict=True, expected_version="1.0.0")'), source.index("def load_data():"))
        self.assertIn('if INTEGRITY.get("status") != "PASS"', source)

    def test_dashboard_runs_data_contract_before_rendering_title(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertLess(source.index("validate_dashboard_data(patients, renal, clinical, landmarks)"), source.index('st.title("PALIC Renal Intelligence")'))


if __name__ == "__main__":
    unittest.main()
