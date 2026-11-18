"""Pure helpers for consistent dashboard navigation and patient-level views.

No Streamlit dependency: selection, filtering and export behavior remain
unit-testable without starting the web application.
"""
from __future__ import annotations

import pandas as pd


class DashboardInteractionError(ValueError):
    """Raised when a dashboard selection cannot be resolved unambiguously."""


def available_patient_ids(patients: pd.DataFrame) -> list[str]:
    """Return stable, non-empty patient identifiers for selection controls."""
    if "patient_id" not in patients.columns:
        raise DashboardInteractionError("La tabla de pacientes no contiene patient_id")
    ids = patients["patient_id"]
    if ids.isna().any():
        raise DashboardInteractionError("Hay identificadores de paciente nulos")
    normalized = ids.astype(str).str.strip()
    if normalized.eq("").any():
        raise DashboardInteractionError("Hay identificadores de paciente vacíos")
    if normalized.duplicated().any():
        raise DashboardInteractionError("La tabla de pacientes contiene identificadores duplicados")
    return sorted(normalized.tolist())


def get_patient_view(
    patient_id: str,
    patients: pd.DataFrame,
    renal: pd.DataFrame,
    clinical: pd.DataFrame,
    landmarks: pd.DataFrame,
) -> dict[str, object]:
    """Resolve one patient consistently across all dashboard source tables.

    Returns defensive copies. Zero or one clinical/landmark row is allowed;
    multiple master, clinical or landmark rows are rejected as ambiguous.
    Renal measurements are returned in chronological order.
    """
    selected = str(patient_id).strip()
    if not selected:
        raise DashboardInteractionError("Debe seleccionar un identificador de paciente")
    for label, frame in (("patients", patients), ("renal", renal),
                         ("clinical", clinical), ("landmarks", landmarks)):
        if "patient_id" not in frame.columns:
            raise DashboardInteractionError(f"La tabla {label} no contiene patient_id")

    master = patients.loc[patients["patient_id"].astype(str).str.strip().eq(selected)].copy()
    if len(master) != 1:
        raise DashboardInteractionError(
            "El paciente seleccionado no existe o no tiene una fila maestra única"
        )
    clinical_rows = clinical.loc[
        clinical["patient_id"].astype(str).str.strip().eq(selected)
    ].copy()
    if len(clinical_rows) > 1:
        raise DashboardInteractionError("El paciente tiene múltiples filas clínicas")
    landmark_rows = landmarks.loc[
        landmarks["patient_id"].astype(str).str.strip().eq(selected)
    ].copy()
    if len(landmark_rows) > 1:
        raise DashboardInteractionError("El paciente tiene múltiples landmarks")
    renal_rows = renal.loc[
        renal["patient_id"].astype(str).str.strip().eq(selected)
    ].copy()
    if "measurement_date" in renal_rows.columns:
        renal_rows["measurement_date"] = pd.to_datetime(
            renal_rows["measurement_date"], errors="coerce"
        )
        if renal_rows["measurement_date"].isna().any():
            raise DashboardInteractionError("El paciente tiene fechas de medición inválidas")
        renal_rows = renal_rows.sort_values(
            ["measurement_date"] + (["measurement_sequence"] if "measurement_sequence" in renal_rows.columns else []),
            kind="stable",
        ).reset_index(drop=True)
    return {
        "patient_id": selected,
        "patient": master.reset_index(drop=True),
        "renal": renal_rows.reset_index(drop=True),
        "clinical": clinical_rows.reset_index(drop=True),
        "landmark": landmark_rows.reset_index(drop=True),
        "has_renal_measurements": not renal_rows.empty,
        "has_clinical_record": len(clinical_rows) == 1,
        "has_landmark": len(landmark_rows) == 1,
    }


def csv_bytes(frame: pd.DataFrame) -> bytes:
    """Serialize a table consistently for downloads, without an index column."""
    if not isinstance(frame, pd.DataFrame):
        raise DashboardInteractionError("La exportación CSV requiere una tabla")
    if frame.columns.duplicated().any():
        raise DashboardInteractionError("No se puede exportar una tabla con columnas duplicadas")
    try:
        return frame.to_csv(index=False).encode("utf-8-sig")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise DashboardInteractionError("No fue posible generar la exportación CSV") from exc
