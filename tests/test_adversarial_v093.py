"""Adversarial tests for v0.9.3 dashboard navigation and patient views."""
import ast
import unittest
from pathlib import Path

import pandas as pd

from src.dashboard.interactions import (
    DashboardInteractionError, available_patient_ids, get_patient_view, csv_bytes,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "generated"


class DashboardInteractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patients = pd.read_csv(DATA / "patients_synthetic.csv")
        cls.renal = pd.read_csv(DATA / "renal_measurements_synthetic.csv", parse_dates=["measurement_date"])
        cls.clinical = pd.read_csv(DATA / "clinical_variables_synthetic.csv")
        cls.landmarks = pd.read_csv(DATA / "longitudinal_landmarks_synthetic.csv", parse_dates=["index_date"])

    def test_patient_ids_are_sorted_and_unique(self):
        ids = available_patient_ids(self.patients)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 500)

    def test_patient_ids_reject_missing_column(self):
        with self.assertRaises(DashboardInteractionError):
            available_patient_ids(pd.DataFrame({"id": ["SYN-1"]}))

    def test_patient_ids_reject_null_and_blank(self):
        for values in (["SYN-1", None], ["SYN-1", "  "]):
            with self.subTest(values=values), self.assertRaises(DashboardInteractionError):
                available_patient_ids(pd.DataFrame({"patient_id": values}))

    def test_patient_ids_reject_duplicates(self):
        with self.assertRaises(DashboardInteractionError):
            available_patient_ids(pd.DataFrame({"patient_id": ["SYN-1", "SYN-1"]}))

    def test_patient_view_filters_all_tables_to_same_patient(self):
        selected = available_patient_ids(self.patients)[0]
        view = get_patient_view(selected, self.patients, self.renal, self.clinical, self.landmarks)
        for key in ("patient", "renal", "clinical", "landmark"):
            self.assertTrue(view[key]["patient_id"].astype(str).eq(selected).all())

    def test_patient_view_returns_single_master_clinical_and_landmark(self):
        selected = available_patient_ids(self.patients)[0]
        view = get_patient_view(selected, self.patients, self.renal, self.clinical, self.landmarks)
        self.assertEqual(len(view["patient"]), 1)
        self.assertEqual(len(view["clinical"]), 1)
        self.assertEqual(len(view["landmark"]), 1)

    def test_patient_view_sorts_measurements_chronologically(self):
        selected = available_patient_ids(self.patients)[0]
        shuffled = self.renal.sample(frac=1, random_state=7)
        view = get_patient_view(selected, self.patients, shuffled, self.clinical, self.landmarks)
        dates = view["renal"]["measurement_date"]
        self.assertTrue(dates.is_monotonic_increasing)

    def test_patient_view_rejects_unknown_patient(self):
        with self.assertRaises(DashboardInteractionError):
            get_patient_view("SYN-NOT-FOUND", self.patients, self.renal, self.clinical, self.landmarks)

    def test_patient_view_rejects_ambiguous_master_patient(self):
        broken = pd.concat([self.patients, self.patients.iloc[[0]]], ignore_index=True)
        selected = str(self.patients.iloc[0].patient_id)
        with self.assertRaises(DashboardInteractionError):
            get_patient_view(selected, broken, self.renal, self.clinical, self.landmarks)

    def test_patient_view_rejects_multiple_landmarks(self):
        broken = pd.concat([self.landmarks, self.landmarks.iloc[[0]]], ignore_index=True)
        selected = str(self.landmarks.iloc[0].patient_id)
        with self.assertRaises(DashboardInteractionError):
            get_patient_view(selected, self.patients, self.renal, self.clinical, broken)

    def test_patient_view_rejects_multiple_clinical_rows(self):
        broken = pd.concat([self.clinical, self.clinical.iloc[[0]]], ignore_index=True)
        selected = str(self.clinical.iloc[0].patient_id)
        with self.assertRaises(DashboardInteractionError):
            get_patient_view(selected, self.patients, self.renal, broken, self.landmarks)

    def test_patient_view_rejects_invalid_measurement_date(self):
        selected = str(self.renal.iloc[0].patient_id)
        broken = self.renal.copy()
        broken["measurement_date"] = broken["measurement_date"].astype("object")
        idx = broken.index[broken.patient_id.astype(str).eq(selected)][0]
        broken.loc[idx, "measurement_date"] = "invalid-date"
        with self.assertRaises(DashboardInteractionError):
            get_patient_view(selected, self.patients, broken, self.clinical, self.landmarks)

    def test_csv_export_is_utf8_without_index(self):
        payload = csv_bytes(pd.DataFrame({"columna": ["demostración"]}))
        self.assertTrue(payload.startswith(b"\xef\xbb\xbf"))
        decoded = payload.decode("utf-8-sig")
        self.assertIn("demostración", decoded)
        self.assertNotIn("Unnamed: 0", decoded)

    def test_csv_export_rejects_duplicate_columns(self):
        frame = pd.DataFrame([[1, 2]], columns=["x", "x"])
        with self.assertRaises(DashboardInteractionError):
            csv_bytes(frame)

    def test_app_uses_shared_patient_view_helpers(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                    and node.module == "src.dashboard.interactions" for alias in node.names}
        self.assertTrue({"available_patient_ids", "get_patient_view", "csv_bytes"} <= imported)
        self.assertGreaterEqual(source.count("get_patient_view("), 2)
        self.assertNotIn('future.to_csv(index=False).encode("utf-8")', source)


if __name__ == "__main__":
    unittest.main()
