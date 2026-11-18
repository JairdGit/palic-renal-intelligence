"""Non-clinical integrity checks linking source renal records to generated landmarks."""
from __future__ import annotations

import pandas as pd
import numpy as np

HORIZON_DAYS = 365
MIN_CONFIRMATION_GAP_DAYS = 30


def validate_landmark_traceability(renal: pd.DataFrame, landmarks: pd.DataFrame) -> dict:
    """Audit source-to-landmark lineage without changing either input frame.

    This validates the demo output contract only; it is not clinical validation.
    """
    required_source = {"patient_id", "measurement_date", "egfr_ml_min_1_73m2"}
    required_output = {
        "patient_id", "index_date", "index_egfr", "cross_date", "confirmation_date",
        "target_sustained_40_raw", "future_valid_tfg_count", "last_future_date",
        "evaluable_365", "observation_status", "target_sustained_40",
    }
    missing_source = sorted(required_source - set(renal.columns))
    missing_output = sorted(required_output - set(landmarks.columns))
    if missing_source or missing_output:
        return {"all_checks_passed": False, "checks": [{
            "check": "required_columns", "passed": False,
            "missing_source": missing_source, "missing_output": missing_output,
        }]}

    r = renal.copy()
    o = landmarks.copy()
    r["measurement_date"] = pd.to_datetime(r["measurement_date"], errors="coerce", utc=True)
    o["index_date"] = pd.to_datetime(o["index_date"], errors="coerce", utc=True)
    o["last_future_date"] = pd.to_datetime(o["last_future_date"], errors="coerce", utc=True)
    o["cross_date"] = pd.to_datetime(o["cross_date"], errors="coerce", utc=True)
    o["confirmation_date"] = pd.to_datetime(o["confirmation_date"], errors="coerce", utc=True)
    r["egfr_ml_min_1_73m2"] = pd.to_numeric(r["egfr_ml_min_1_73m2"], errors="coerce")
    o["index_egfr"] = pd.to_numeric(o["index_egfr"], errors="coerce")
    o["future_valid_tfg_count"] = pd.to_numeric(o["future_valid_tfg_count"], errors="coerce")
    o["target_sustained_40_raw"] = pd.to_numeric(o["target_sustained_40_raw"], errors="coerce")

    source_ids = set(r["patient_id"].dropna())
    output_ids = set(o["patient_id"].dropna())
    duplicate_output = int(o["patient_id"].duplicated().sum())
    missing_output_ids = len(source_ids - output_ids)
    orphan_output_ids = len(output_ids - source_ids)

    index_matches = 0
    index_mismatches = 0
    future_count_mismatches = 0
    last_date_mismatches = 0
    event_mismatches = 0
    evaluability_mismatches = 0
    status_mismatches = 0
    target_policy_mismatches = 0
    chronology_mismatches = 0

    for row in o.itertuples(index=False):
        pid = row.patient_id
        if pd.isna(pid) or pd.isna(row.index_date) or not np.isfinite(row.index_egfr):
            index_mismatches += 1
            continue
        patient = r[r.patient_id == pid]
        index_rows = patient[(patient.measurement_date == row.index_date) &
                             np.isclose(patient.egfr_ml_min_1_73m2, row.index_egfr, equal_nan=False)]
        if index_rows.empty:
            index_mismatches += 1
        else:
            index_matches += 1

        future = patient[(patient.measurement_date > row.index_date) &
                         (patient.measurement_date <= row.index_date + pd.Timedelta(days=HORIZON_DAYS)) &
                         patient.measurement_date.notna() &
                         patient.egfr_ml_min_1_73m2.notna()]
        expected_count = len(future)
        if pd.isna(row.future_valid_tfg_count) or int(row.future_valid_tfg_count) != expected_count:
            future_count_mismatches += 1
        expected_last = future.measurement_date.max() if expected_count else pd.NaT
        if (pd.isna(expected_last) != pd.isna(row.last_future_date)) or (
            pd.notna(expected_last) and expected_last != row.last_future_date
        ):
            last_date_mismatches += 1
        expected_evaluable = expected_count >= 2
        if bool(row.evaluable_365) != expected_evaluable:
            evaluability_mismatches += 1
        expected_status = "EVALUABLE" if expected_evaluable else "CENSORED_NON_EVALUABLE"
        if row.observation_status != expected_status:
            status_mismatches += 1
        if (not expected_evaluable and pd.notna(row.target_sustained_40)) or (
            expected_evaluable and pd.isna(row.target_sustained_40)
        ):
            target_policy_mismatches += 1

        has_event_dates = pd.notna(row.cross_date) or pd.notna(row.confirmation_date)
        raw_event = row.target_sustained_40_raw == 1
        if bool(raw_event) != bool(has_event_dates):
            event_mismatches += 1
        if raw_event:
            if pd.isna(row.cross_date) or pd.isna(row.confirmation_date):
                event_mismatches += 1
            else:
                gap = (row.confirmation_date - row.cross_date).days
                if (row.cross_date <= row.index_date or
                    row.confirmation_date < row.cross_date + pd.Timedelta(days=MIN_CONFIRMATION_GAP_DAYS) or
                    row.confirmation_date > row.index_date + pd.Timedelta(days=HORIZON_DAYS)):
                    chronology_mismatches += 1
                cross_values = future.loc[future.measurement_date == row.cross_date, "egfr_ml_min_1_73m2"]
                confirm_values = future.loc[future.measurement_date == row.confirmation_date, "egfr_ml_min_1_73m2"]
                threshold = row.index_egfr * 0.60
                if cross_values.empty or confirm_values.empty or not (cross_values <= threshold).any() or not (confirm_values <= threshold).any() or gap < MIN_CONFIRMATION_GAP_DAYS:
                    event_mismatches += 1
        if expected_evaluable and pd.notna(row.target_sustained_40):
            if int(row.target_sustained_40) != int(row.target_sustained_40_raw):
                target_policy_mismatches += 1

    checks = [
        {"check": "one_landmark_per_patient", "passed": duplicate_output == 0, "duplicate_landmarks": duplicate_output},
        {"check": "source_output_patient_coverage", "passed": missing_output_ids == 0 and orphan_output_ids == 0,
         "source_patients_without_landmark": missing_output_ids, "landmark_patients_without_source": orphan_output_ids},
        {"check": "index_record_lineage", "passed": index_mismatches == 0,
         "matched_index_records": index_matches, "index_record_mismatches": index_mismatches},
        {"check": "future_observation_count", "passed": future_count_mismatches == 0, "mismatches": future_count_mismatches},
        {"check": "last_future_date", "passed": last_date_mismatches == 0, "mismatches": last_date_mismatches},
        {"check": "evaluability_consistency", "passed": evaluability_mismatches == 0, "mismatches": evaluability_mismatches},
        {"check": "observation_status_consistency", "passed": status_mismatches == 0, "mismatches": status_mismatches},
        {"check": "event_confirmation_lineage", "passed": event_mismatches == 0, "mismatches": event_mismatches},
        {"check": "event_temporal_bounds", "passed": chronology_mismatches == 0, "mismatches": chronology_mismatches},
        {"check": "censoring_target_policy", "passed": target_policy_mismatches == 0, "mismatches": target_policy_mismatches,
         "description": "Non-evaluable targets must remain missing; evaluable targets must agree with the raw event flag."},
    ]
    return {"all_checks_passed": all(c["passed"] for c in checks), "checks_passed": sum(c["passed"] for c in checks),
            "checks_total": len(checks), "checks": checks,
            "scope": "synthetic source-to-landmark traceability; not clinical validation"}
