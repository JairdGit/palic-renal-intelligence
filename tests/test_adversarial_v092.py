"""Adversarial tests for v0.9.2 dashboard presentation contracts."""
import ast
import json
import unittest
from pathlib import Path

import pandas as pd

from src.dashboard.presentation import (
    DashboardPresentationError,
    build_summary,
    build_scenario_counts,
    build_frequency_summary,
    safe_export_filename,
    json_bytes,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "generated"


class DashboardPresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patients = pd.read_csv(DATA / "patients_synthetic.csv")
        cls.renal = pd.read_csv(DATA / "renal_measurements_synthetic.csv", parse_dates=["measurement_date"])
        cls.landmarks = pd.read_csv(DATA / "longitudinal_landmarks_synthetic.csv")

    def test_summary_matches_generated_artifacts(self):
        result = build_summary(self.patients, self.renal, self.landmarks)
        self.assertEqual(result["patients"], 500)
        self.assertEqual(result["renal_measurements"], 4293)
        self.assertEqual(result["landmarks"], 500)
        self.assertEqual(result["evaluable_365"], 347)
        self.assertEqual(result["non_evaluable_365"], 153)
        self.assertEqual(result["events_evaluable"] + result["no_event_evaluable"], 347)

    def test_summary_rejects_landmark_count_mismatch(self):
        with self.assertRaises(DashboardPresentationError):
            build_summary(self.patients, self.renal, self.landmarks.iloc[:-1])

    def test_summary_rejects_non_null_censored_target(self):
        broken = self.landmarks.copy()
        idx = pd.to_numeric(broken.evaluable_365, errors="coerce").eq(0).idxmax()
        broken.loc[idx, "target_sustained_40"] = 0
        with self.assertRaises(DashboardPresentationError):
            build_summary(self.patients, self.renal, broken)

    def test_summary_rejects_non_binary_evaluable_flag_by_reconciliation(self):
        broken = self.landmarks.copy()
        broken["evaluable_365"] = broken["evaluable_365"].astype(object)
        broken.loc[0, "evaluable_365"] = 2
        with self.assertRaises(DashboardPresentationError):
            build_summary(self.patients, self.renal, broken)

    def test_scenario_counts_reconcile_to_patients(self):
        counts = build_scenario_counts(self.patients)
        self.assertEqual(int(counts.Pacientes.sum()), len(self.patients))
        self.assertEqual(list(counts.columns), ["Escenario", "Pacientes"])

    def test_scenario_counts_handle_missing_scenario_explicitly(self):
        frame = pd.DataFrame({"scenario": ["A", None, "A"]})
        result = build_scenario_counts(frame)
        self.assertEqual(int(result.Pacientes.sum()), 3)
        self.assertIn("SIN_ESCENARIO", set(result.Escenario))

    def test_frequency_summary_has_nonnegative_intervals(self):
        result = build_frequency_summary(self.renal)
        self.assertTrue((result["Intervalos"] >= 0).all())
        self.assertTrue((result["Mediana días"].dropna() >= 0).all())

    def test_frequency_summary_rejects_invalid_dates(self):
        broken = pd.DataFrame({"patient_id": ["SYN-1", "SYN-1"],
                               "measurement_date": ["2026-01-01", "not-a-date"],
                               "synthetic_scenario": ["A", "A"]})
        with self.assertRaises(DashboardPresentationError):
            build_frequency_summary(broken)

    def test_export_filename_sanitizes_path_and_special_characters(self):
        name = safe_export_filename("../../SYN-001/../../evil", "auditoria futura", "CSV")
        self.assertNotIn("/", name)
        self.assertNotIn("..", name)
        self.assertTrue(name.endswith("_auditoria_futura.csv"))

    def test_export_filename_rejects_empty_after_sanitization(self):
        with self.assertRaises(DashboardPresentationError):
            safe_export_filename("../../", "audit", "csv")

    def test_json_export_is_utf8_and_rejects_nonfinite_values(self):
        payload = json_bytes({"estado": "aprobado", "nota": "demostración"})
        self.assertEqual(json.loads(payload.decode("utf-8"))["nota"], "demostración")
        with self.assertRaises(DashboardPresentationError):
            json_bytes({"metric": float("nan")})

    def test_app_uses_testable_presentation_helpers(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imported = {alias.name for node in imports if node.module == "src.dashboard.presentation" for alias in node.names}
        self.assertTrue({"build_summary", "build_scenario_counts", "build_frequency_summary", "safe_export_filename", "json_bytes"} <= imported)
        for section in ["Resumen", "Trayectorias", "Auditoría por paciente", "Inteligencia de riesgo", "Calidad de datos", "Trazabilidad"]:
            self.assertIn(section, source)


if __name__ == "__main__":
    unittest.main()
