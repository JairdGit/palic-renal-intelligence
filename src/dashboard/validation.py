"""Cross-artifact contract checks performed before dashboard rendering."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
import pandas as pd


@dataclass(frozen=True)
class DashboardCheck:
    name: str
    passed: bool
    observed: Any
    expected: str
    severity: str = "high"


class DashboardDataContractError(ValueError):
    def __init__(self, checks: list[DashboardCheck]):
        self.checks = checks
        failed = [c.name for c in checks if not c.passed]
        super().__init__("Contrato de datos del dashboard incumplido: " + ", ".join(failed))


def validate_dashboard_data(patients: pd.DataFrame, renal: pd.DataFrame,
                            clinical: pd.DataFrame, landmarks: pd.DataFrame) -> dict:
    """Validate identity, coverage, outcome and synthetic-only invariants.

    This is a display-integrity gate, not clinical validation.
    """
    checks: list[DashboardCheck] = []

    def add(name: str, passed: bool, observed: Any, expected: str, severity="high"):
        checks.append(DashboardCheck(name, bool(passed), observed, expected, severity))

    required = {
        "patients": {"patient_id"},
        "renal": {"patient_id", "measurement_date", "egfr_ml_min_1_73m2"},
        "clinical": {"patient_id"},
        "landmarks": {"patient_id", "evaluable_365", "target_sustained_40"},
    }
    frames = {"patients": patients, "renal": renal, "clinical": clinical, "landmarks": landmarks}
    for name, frame in frames.items():
        missing = sorted(required[name] - set(frame.columns))
        add(f"{name}_required_columns", not missing, missing, "ninguna columna obligatoria ausente")
    if any(not c.passed for c in checks):
        raise DashboardDataContractError(checks)

    for name, frame in frames.items():
        ids = frame["patient_id"].astype("string")
        add(f"{name}_nonempty_ids", bool(ids.notna().all() and ids.str.strip().ne("").all()),
            int(ids.isna().sum() + ids.str.strip().eq("").sum()), "todos los identificadores presentes")

    pids = set(patients.patient_id.astype(str))
    for name in ("clinical", "landmarks"):
        ids = set(frames[name].patient_id.astype(str))
        add(f"{name}_identity_match", ids == pids,
            {"missing": len(pids - ids), "unexpected": len(ids - pids)}, "identidades iguales a pacientes")
    renal_ids = set(renal.patient_id.astype(str))
    add("renal_no_orphan_patients", renal_ids <= pids,
        len(renal_ids - pids), "todas las mediciones pertenecen a pacientes maestros")
    add("patient_ids_synthetic", bool(patients.patient_id.astype(str).str.startswith("SYN-").all()),
        int((~patients.patient_id.astype(str).str.startswith("SYN-")).sum()), "todos comienzan por SYN-")
    add("patient_ids_unique", bool(patients.patient_id.is_unique),
        int(patients.patient_id.duplicated().sum()), "un registro maestro por paciente")
    add("landmark_ids_unique", bool(landmarks.patient_id.is_unique),
        int(landmarks.patient_id.duplicated().sum()), "un landmark por paciente")
    evaluable_values = pd.to_numeric(landmarks.evaluable_365, errors="coerce")
    add("evaluable_flag_binary", bool(evaluable_values.notna().all() and evaluable_values.isin([0, 1]).all()),
        int((evaluable_values.isna() | ~evaluable_values.isin([0, 1])).sum()), "bandera evaluable en {0,1}")
    evaluable = evaluable_values.eq(1)
    target = pd.to_numeric(landmarks.target_sustained_40, errors="coerce")
    add("evaluable_targets_binary", bool(target.loc[evaluable].isin([0, 1]).all()),
        sorted(map(str, target.loc[evaluable].dropna().unique())), "objetivos evaluables en {0,1}")
    add("censored_targets_null", bool(target.loc[~evaluable].isna().all()),
        int(target.loc[~evaluable].notna().sum()), "objetivo nulo para no evaluables")
    add("landmark_counts_reconcile", len(landmarks) == len(patients),
        {"patients": len(patients), "landmarks": len(landmarks)}, "un landmark por paciente")
    report = {"checks": [asdict(c) for c in checks],
              "checks_passed": sum(c.passed for c in checks),
              "checks_total": len(checks),
              "all_checks_passed": all(c.passed for c in checks),
              "scope": "dashboard data contract; synthetic demonstration only"}
    if not report["all_checks_passed"]:
        raise DashboardDataContractError(checks)
    return report
