import pandas as pd

def audit_patient_outcome(renal, landmark_row, horizon_days=365, confirmation_days=30):
    """Explain the implemented sustained-decline rule for one synthetic patient."""
    pid = landmark_row["patient_id"]
    index_date = pd.to_datetime(landmark_row["index_date"])
    index_egfr = float(landmark_row["index_egfr"])
    threshold = index_egfr * 0.60
    h = renal.loc[renal.patient_id == pid].copy()
    h["measurement_date"] = pd.to_datetime(h["measurement_date"], errors="coerce")
    h["egfr_ml_min_1_73m2"] = pd.to_numeric(h["egfr_ml_min_1_73m2"], errors="coerce")
    future = h.loc[
        h.measurement_date.gt(index_date)
        & h.measurement_date.le(index_date + pd.Timedelta(days=horizon_days))
    ].dropna(subset=["measurement_date", "egfr_ml_min_1_73m2"]).sort_values("measurement_date")
    evaluable = len(future) >= 2
    below = future.loc[future.egfr_ml_min_1_73m2.le(threshold)]
    cross_date = None
    confirmation_date = None
    status = "NON_EVALUABLE"
    explanation = "Horizonte no evaluable: se requieren al menos dos mediciones futuras válidas."
    if evaluable:
        status = "EVALUABLE_NO_EVENT"
        explanation = "No se identificó un cruce del umbral del 60 % de la TFG índice."
        for _, cross in below.iterrows():
            later = below.loc[below.measurement_date.ge(cross.measurement_date + pd.Timedelta(days=confirmation_days))]
            if not later.empty:
                cross_date = cross.measurement_date
                confirmation_date = later.iloc[0].measurement_date
                status = "EVENT_CONFIRMED"
                explanation = "Se identificó una medición bajo el umbral y otra medición también bajo el umbral al menos 30 días después."
                break
        if status != "EVENT_CONFIRMED" and not below.empty:
            cross_date = below.iloc[0].measurement_date
            status = "CROSSING_NOT_CONFIRMED"
            explanation = "Se observó un cruce del umbral, pero no una segunda medición calificadora al menos 30 días después."
    days = None
    if cross_date is not None and confirmation_date is not None:
        days = int((confirmation_date - cross_date).days)
    future = future.assign(
        days_from_landmark=(future.measurement_date - index_date).dt.days,
        threshold_60pct=threshold
    )
    return {
        "patient_id": pid, "index_date": index_date, "index_egfr": index_egfr,
        "threshold_60pct": threshold, "future_valid_measurements": len(future),
        "evaluable_365": evaluable, "status": status, "explanation": explanation,
        "cross_date": cross_date, "confirmation_date": confirmation_date,
        "confirmation_gap_days": days, "future_observations": future
    }
