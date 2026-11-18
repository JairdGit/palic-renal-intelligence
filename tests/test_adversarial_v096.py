"""Four-surface adversarial tests for operational diagnostics in v0.9.6."""
import tempfile
import unittest
from pathlib import Path

from src.dashboard.diagnostics import (
    DashboardDiagnosticsError, REQUIRED_ARTIFACTS, build_operational_diagnostics,
)


class OperationalDiagnosticsV096(unittest.TestCase):
    def _root(self, base: Path):
        for relative in REQUIRED_ARTIFACTS:
            target = base / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("artifact", encoding="utf-8")
        return base

    def test_all_required_artifacts_and_manifest_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            result = build_operational_diagnostics(root, {"status": "PASS", "verified": 7})
            self.assertEqual(result["status"], "OPERATIVO_DEMO")
            self.assertEqual(result["checks_passed"], 8)

    def test_missing_artifact_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            (root / "data/generated/quality_report.json").unlink()
            result = build_operational_diagnostics(root, {"status": "PASS", "verified": 7})
            self.assertEqual(result["status"], "BLOQUEADO")
            self.assertEqual(result["failures"], 1)

    def test_empty_artifact_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            (root / "data/generated/longitudinal_audit.json").write_text("", encoding="utf-8")
            result = build_operational_diagnostics(root, {"status": "PASS", "verified": 7})
            self.assertEqual(result["status"], "BLOQUEADO")

    def test_manifest_failure_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            result = build_operational_diagnostics(root, {"status": "FAIL", "verified": 6})
            self.assertEqual(result["status"], "BLOQUEADO")
            self.assertEqual(result["checks"][-1]["status"], "FAIL")

    def test_missing_manifest_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            result = build_operational_diagnostics(root, {"status": "MISSING_MANIFEST", "verified": 0})
            self.assertEqual(result["status"], "BLOQUEADO")

    def test_invalid_integrity_status_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DashboardDiagnosticsError):
                build_operational_diagnostics(Path(tmp), {"status": "UNKNOWN"})

    def test_non_dictionary_integrity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DashboardDiagnosticsError):
                build_operational_diagnostics(Path(tmp), None)

    def test_scope_does_not_claim_clinical_validity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            result = build_operational_diagnostics(root, {"status": "PASS", "verified": 7})
            self.assertIn("no valida uso clínico", result["scope"])
            self.assertNotIn("validado clínicamente", result["scope"])

    def test_diagnostics_includes_exact_artifact_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            result = build_operational_diagnostics(root, {"status": "PASS", "verified": 7})
            self.assertEqual([x["artifact"] for x in result["checks"][:-1]], list(REQUIRED_ARTIFACTS))

    def test_manifest_check_is_always_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            result = build_operational_diagnostics(root, {"status": "PASS", "verified": 7})
            self.assertEqual(result["checks"][-1]["artifact"], "Verificación SHA-256 del manifiesto")


if __name__ == "__main__":
    unittest.main()
