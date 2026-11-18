"""Adversarial tests for v0.9.8 demo acceptance and presentation readiness."""
import shutil
import tempfile
import unittest
from pathlib import Path

from src.dashboard.demo_acceptance import DemoAcceptanceError, build_demo_acceptance
from src.dashboard.demo_journey import build_demo_journey

ROOT = Path(__file__).resolve().parents[1]
INTEGRITY = {"status": "PASS", "verified": 80}
OPERATIONAL = {"status": "OPERATIVO_DEMO", "checks_passed": 8, "checks_total": 8}
CONTRACT = {"all_checks_passed": True, "checks_passed": 12, "checks_total": 12}


class DemoAcceptanceV098(unittest.TestCase):
    def build(self, **overrides):
        args = dict(root=ROOT, integrity=INTEGRITY, operational=OPERATIONAL,
                    data_contract=CONTRACT, journey=build_demo_journey())
        args.update(overrides)
        return build_demo_acceptance(**args)

    def test_canonical_demo_is_ready(self):
        self.assertEqual(self.build()["status"], "READY_FOR_GUIDED_DEMO")

    def test_acceptance_has_six_controls(self):
        result = self.build()
        self.assertEqual(result["checks_total"], 6)
        self.assertEqual(result["checks_passed"], 6)

    def test_integrity_failure_blocks_readiness(self):
        result = self.build(integrity={"status": "FAIL", "verified": 79})
        self.assertEqual(result["status"], "NOT_READY")
        self.assertIn("integridad_sha256", result["failures"])

    def test_operational_failure_blocks_readiness(self):
        result = self.build(operational={"status": "BLOQUEADO", "checks_passed": 7, "checks_total": 8})
        self.assertIn("artefactos_operativos", result["failures"])

    def test_data_contract_failure_blocks_readiness(self):
        result = self.build(data_contract={"all_checks_passed": False, "checks_passed": 11, "checks_total": 12})
        self.assertIn("contrato_datos_dashboard", result["failures"])

    def test_wrong_duration_blocks_readiness(self):
        journey = build_demo_journey()
        journey["total_minutes"] = 16
        result = self.build(journey=journey)
        self.assertIn("recorrido_seis_secciones_15_min", result["failures"])

    def test_reordered_route_blocks_readiness(self):
        journey = build_demo_journey()
        journey["sections"] = list(reversed(journey["sections"]))
        result = self.build(journey=journey)
        self.assertIn("recorrido_seis_secciones_15_min", result["failures"])

    def test_missing_disclaimer_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src" / "dashboard").mkdir(parents=True)
            shutil.copy(ROOT / "src" / "dashboard" / "demo_exports.py", root / "src" / "dashboard" / "demo_exports.py")
            (root / "app.py").write_text("Datos 100 % sintéticos; no diagnostica", encoding="utf-8")
            result = self.build(root=root)
            self.assertIn("declaraciones_de_seguridad_y_alcance", result["failures"])

    def test_missing_export_function_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src" / "dashboard").mkdir(parents=True)
            shutil.copy(ROOT / "app.py", root / "app.py")
            (root / "src" / "dashboard" / "demo_exports.py").write_text("def csv_export_with_provenance(): pass", encoding="utf-8")
            result = self.build(root=root)
            self.assertIn("exportaciones_con_procedencia", result["failures"])

    def test_invalid_integrity_input_raises(self):
        with self.assertRaises(DemoAcceptanceError):
            self.build(integrity=None)

    def test_invalid_data_contract_input_raises(self):
        with self.assertRaises(DemoAcceptanceError):
            self.build(data_contract=[])

    def test_missing_app_source_raises(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(DemoAcceptanceError):
                self.build(root=Path(temp))

    def test_checklist_does_not_claim_browser_or_clinical_validation(self):
        result = self.build()
        self.assertEqual(result["browser_visual_test"], "NOT_ASSESSED_BY_THIS_CHECKLIST")
        self.assertFalse(result["clinical_validation"])
        self.assertFalse(result["predictive_model_connected"])

    def test_generator_version_is_incremented(self):
        source = (ROOT / "run_demo.py").read_text(encoding="utf-8")
        self.assertIn("generator_version'] = 'v1.0.0'", source)


if __name__ == "__main__":
    unittest.main()
