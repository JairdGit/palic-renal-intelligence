"""Reconcile individual longitudinal records with aggregate demo reports.

Synthetic demonstration control only; this is not clinical validation.
"""
from __future__ import annotations

import pandas as pd


def _is_true(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def reconcile_aggregate_outputs(
    patients: pd.DataFrame,
    renal: pd.DataFrame,
    clinical: pd.DataFrame,
    landmarks: pd.DataFrame,
    quality_report: dict,
    longitudinal_audit: dict,
) -> dict:
    """Check denominators, event/censoring counts and report-to-row agreement."""
    required = {
        "patient_id", "evaluable_365", "target_sustained_40",
        "target_sustained_40_raw", "observation_status",
    }
    missing = sorted(required - set(landmarks.columns))
    if missing:
        return {"all_checks_passed": False, "checks_passed": 0, "checks_total": 1,
                "checks": [{"check": "landmark_columns", "passed": False, "missing": missing}],
                "scope": "synthetic aggregate reconciliation; not clinical validation"}

    evaluable = _is_true(landmarks["evaluable_365"])
    target = pd.to_numeric(landmarks["target_sustained_40"], errors="coerce")
    raw_target = pd.to_numeric(landmarks["target_sustained_40_raw"], errors="coerce")
    observed_events = int((target == 1).sum())
    raw_events = int((raw_target == 1).sum())
    evaluable_count = int(evaluable.sum())
    non_evaluable_count = int((~evaluable).sum())
    missing_targets = int(target.isna().sum())
    evaluable_no_event = int((evaluable & target.eq(0)).sum())
    event_evaluable = int((evaluable & target.eq(1)).sum())
    status_counts = landmarks["observation_status"].astype(str).value_counts().to_dict()

    observed = {
        "patients": int(len(patients)),
        "renal_measurements": int(len(renal)),
        "clinical_variables": int(len(clinical)),
        "landmarks": int(len(landmarks)),
        "unique_landmark_patients": int(landmarks.patient_id.nunique(dropna=True)),
        "evaluable_365": evaluable_count,
        "non_evaluable_365": non_evaluable_count,
        "events_raw": raw_events,
        "events_evaluable": event_evaluable,
        "evaluable_no_event": evaluable_no_event,
        "missing_targets": missing_targets,
        "status_counts": {str(k): int(v) for k, v in status_counts.items()},
    }

    quality_rows = quality_report.get("row_counts", {})
    checks = []
    def add(name: str, passed: bool, **details):
        checks.append({"check": name, "passed": bool(passed), **details})

    add("quality_row_counts_match", 
        quality_rows.get("patients") == observed["patients"] and
        quality_rows.get("renal_measurements") == observed["renal_measurements"] and
        quality_rows.get("clinical_variables") == observed["clinical_variables"],
        expected=quality_rows, observed={k: observed[k] for k in ("patients", "renal_measurements", "clinical_variables")})
    add("audit_landmark_count_matches", longitudinal_audit.get("landmarks") == observed["landmarks"],
        reported=longitudinal_audit.get("landmarks"), observed=observed["landmarks"])
    add("unique_landmark_patient_count_matches", longitudinal_audit.get("unique_patients") == observed["unique_landmark_patients"],
        reported=longitudinal_audit.get("unique_patients"), observed=observed["unique_landmark_patients"])
    add("evaluable_denominator_matches", longitudinal_audit.get("evaluable_365") == evaluable_count,
        reported=longitudinal_audit.get("evaluable_365"), observed=evaluable_count)
    add("non_evaluable_denominator_matches", longitudinal_audit.get("non_evaluable_365") == non_evaluable_count,
        reported=longitudinal_audit.get("non_evaluable_365"), observed=non_evaluable_count)
    add("raw_event_count_matches", longitudinal_audit.get("events_raw") == raw_events,
        reported=longitudinal_audit.get("events_raw"), observed=raw_events)
    add("evaluable_event_count_matches", longitudinal_audit.get("events_evaluable") == event_evaluable,
        reported=longitudinal_audit.get("events_evaluable"), observed=event_evaluable)
    add("evaluable_partition_is_complete", evaluable_count == event_evaluable + evaluable_no_event,
        evaluable=evaluable_count, events=event_evaluable, no_event=evaluable_no_event)
    add("non_evaluable_targets_remain_missing", int((~evaluable & target.notna()).sum()) == 0,
        non_evaluable_with_target=int((~evaluable & target.notna()).sum()), missing_targets=missing_targets)
    add("evaluable_targets_are_binary", bool(target.loc[evaluable].isin([0, 1]).all()),
        invalid_evaluable_targets=int((~target.loc[evaluable].isin([0, 1])).sum()))
    add("raw_and_evaluable_event_counts_reconcile", raw_events == event_evaluable,
        raw_events=raw_events, evaluable_events=event_evaluable)
    add("landmark_ids_are_unique_and_complete", landmarks.patient_id.notna().all() and not landmarks.patient_id.duplicated().any(),
        null_ids=int(landmarks.patient_id.isna().sum()), duplicate_ids=int(landmarks.patient_id.duplicated().sum()))

    return {
        "all_checks_passed": all(c["passed"] for c in checks),
        "checks_passed": sum(c["passed"] for c in checks),
        "checks_total": len(checks),
        "observed": observed,
        "checks": checks,
        "scope": "synthetic individual-to-aggregate reconciliation; not clinical validation",
    }
