"""Operational diagnostics for the synthetic demo dashboard.

This module reports package/artifact readiness only. It does not assess
clinical validity, model performance, or cybersecurity certification.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Any


class DashboardDiagnosticsError(ValueError):
    """Raised when diagnostic inputs are malformed."""


REQUIRED_ARTIFACTS = (
    "RELEASE_MANIFEST.json",
    "data/generated/patients_synthetic.csv",
    "data/generated/renal_measurements_synthetic.csv",
    "data/generated/clinical_variables_synthetic.csv",
    "data/generated/longitudinal_landmarks_synthetic.csv",
    "data/generated/quality_report.json",
    "data/generated/longitudinal_audit.json",
)


def build_operational_diagnostics(root: str | Path, integrity: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic, fail-closed artifact readiness checks."""
    root_path = Path(root).resolve()
    if not isinstance(integrity, dict):
        raise DashboardDiagnosticsError("El resultado de integridad debe ser un objeto")
    status = integrity.get("status")
    if status not in {"PASS", "FAIL", "MISSING_MANIFEST", "INVALID_MANIFEST"}:
        raise DashboardDiagnosticsError("Estado de integridad desconocido")

    checks: list[dict[str, str]] = []
    for relative in REQUIRED_ARTIFACTS:
        rel = PurePosixPath(relative)
        candidate = (root_path / Path(*rel.parts)).resolve()
        safe = not rel.is_absolute() and all(part not in {"", ".", ".."} for part in rel.parts)
        safe = safe and (root_path == candidate or root_path in candidate.parents)
        exists = safe and candidate.is_file()
        nonempty = bool(exists and candidate.stat().st_size > 0)
        checks.append({
            "artifact": relative,
            "status": "PASS" if nonempty else "FAIL",
            "detail": "Disponible y no vacío" if nonempty else "Ausente, vacío o ruta no permitida",
        })

    integrity_ok = status == "PASS"
    checks.append({
        "artifact": "Verificación SHA-256 del manifiesto",
        "status": "PASS" if integrity_ok else "FAIL",
        "detail": f"{integrity.get('verified', 0)} archivos verificados; estado {status}",
    })
    failures = sum(item["status"] != "PASS" for item in checks)
    return {
        "status": "OPERATIVO_DEMO" if failures == 0 else "BLOQUEADO",
        "checks_passed": len(checks) - failures,
        "checks_total": len(checks),
        "failures": failures,
        "checks": checks,
        "scope": "Disponibilidad de artefactos y verificación de integridad del paquete; no valida uso clínico ni inferencia predictiva.",
    }
