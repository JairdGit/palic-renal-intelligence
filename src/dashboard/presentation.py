"""Pure dashboard presentation helpers; no Streamlit dependency.

These functions keep KPI, chart-table and export calculations testable without
starting the web server. They operate only on already validated synthetic data.
"""
from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd


class DashboardPresentationError(ValueError):
    """Raised when validated dashboard inputs cannot be presented safely."""


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise DashboardPresentationError(f"{label}: faltan columnas: {', '.join(missing)}")


def build_summary(patients: pd.DataFrame, renal: pd.DataFrame,
                  landmarks: pd.DataFrame) -> dict[str, int]:
    """Return reconciled dashboard KPIs using explicit evaluability semantics."""
    _require_columns(patients, {"patient_id"}, "patients")
    _require_columns(renal, {"patient_id"}, "renal")
    _require_columns(landmarks, {"patient_id", "evaluable_365", "target_sustained_40"}, "landmarks")
    evaluable_values = pd.to_numeric(landmarks["evaluable_365"], errors="coerce")
    if evaluable_values.isna().any() or not evaluable_values.isin([0, 1]).all():
        raise DashboardPresentationError("La bandera evaluable_365 debe contener únicamente 0/1")
    evaluable = evaluable_values.eq(1)
    targets = pd.to_numeric(landmarks["target_sustained_40"], errors="coerce")
    events = int(targets.loc[evaluable].eq(1).sum())
    no_event = int(targets.loc[evaluable].eq(0).sum())
    non_evaluable = int((~evaluable).sum())
    summary = {
        "patients": int(len(patients)),
        "renal_measurements": int(len(renal)),
        "landmarks": int(len(landmarks)),
        "evaluable_365": int(evaluable.sum()),
        "non_evaluable_365": non_evaluable,
        "events_evaluable": events,
        "no_event_evaluable": no_event,
    }
    if summary["landmarks"] != summary["patients"]:
        raise DashboardPresentationError("El total de landmarks no coincide con pacientes")
    if summary["evaluable_365"] + summary["non_evaluable_365"] != summary["landmarks"]:
        raise DashboardPresentationError("La evaluabilidad no concilia con el total de landmarks")
    if summary["events_evaluable"] + summary["no_event_evaluable"] != summary["evaluable_365"]:
        raise DashboardPresentationError("Los desenlaces evaluables no concilian")
    if targets.loc[~evaluable].notna().any():
        raise DashboardPresentationError("Los no evaluables deben conservar objetivo nulo")
    return summary


def build_scenario_counts(patients: pd.DataFrame) -> pd.DataFrame:
    _require_columns(patients, {"scenario"}, "patients")
    result = (patients["scenario"].fillna("SIN_ESCENARIO").astype(str)
              .value_counts(dropna=False).rename_axis("Escenario")
              .reset_index(name="Pacientes").sort_values("Escenario", kind="stable")
              .reset_index(drop=True))
    if int(result["Pacientes"].sum()) != len(patients):
        raise DashboardPresentationError("La distribución de escenarios no concilia con pacientes")
    return result


def build_frequency_summary(renal: pd.DataFrame) -> pd.DataFrame:
    _require_columns(renal, {"patient_id", "measurement_date", "synthetic_scenario"}, "renal")
    data = renal[["patient_id", "measurement_date", "synthetic_scenario"]].copy()
    data["measurement_date"] = pd.to_datetime(data["measurement_date"], errors="coerce")
    if data["measurement_date"].isna().any():
        raise DashboardPresentationError("Hay fechas de medición inválidas")
    data = data.sort_values(["patient_id", "measurement_date"], kind="stable")
    data["gap_days"] = data.groupby("patient_id", sort=False)["measurement_date"].diff().dt.total_seconds() / 86400
    grouped = data.groupby("synthetic_scenario", dropna=False)["gap_days"]
    result = grouped.agg(intervals="count", median_days="median", mean_days="mean", max_days="max").reset_index()
    result = result.rename(columns={"synthetic_scenario": "Escenario", "intervals": "Intervalos",
                                    "median_days": "Mediana días", "mean_days": "Promedio días",
                                    "max_days": "Máximo días"})
    result["Escenario"] = result["Escenario"].fillna("SIN_ESCENARIO").astype(str)
    return result.sort_values("Escenario", kind="stable").reset_index(drop=True)


def safe_export_filename(patient_id: str, suffix: str, extension: str) -> str:
    """Constrain download filenames to a conservative ASCII allowlist."""
    patient = re.sub(r"[^A-Za-z0-9_-]+", "_", str(patient_id)).strip("._-")
    tail = re.sub(r"[^A-Za-z0-9_-]+", "_", str(suffix)).strip("._-")
    ext = re.sub(r"[^A-Za-z0-9]+", "", str(extension)).lower()
    if not patient or not tail or not ext:
        raise DashboardPresentationError("Identificador o extensión de exportación inválidos")
    return f"{patient}_{tail}.{ext}"


def json_bytes(payload: dict[str, Any]) -> bytes:
    """Serialize JSON exports while rejecting NaN/Infinity and non-serializable values."""
    try:
        return json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise DashboardPresentationError("El contenido JSON no es válido para exportación") from exc
