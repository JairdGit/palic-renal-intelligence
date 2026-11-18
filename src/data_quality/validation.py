from __future__ import annotations
import pandas as pd
import numpy as np

def validate_datasets(patients, renal, clinical, reference_date=None):
    """Validate synthetic demo tables without treating technical checks as clinical validation."""
    checks = []
    schemas = [
        ("patients", patients, {"patient_id","age_years","sex","region","scenario"}),
        ("renal", renal, {"patient_id","measurement_date","egfr_ml_min_1_73m2","creatinine_mg_dl","measurement_sequence"}),
        ("clinical", clinical, {"patient_id","hypertension_simulated","diabetes_simulated","bmi_simulated"})
    ]
    missing_by_table = {}
    for name, frame, required in schemas:
        missing = sorted(required - set(frame.columns))
        missing_by_table[name] = missing
        checks.append({"check": f"{name}_required_columns", "passed": not missing, "missing": missing})

    if not any(missing_by_table.values()):
        pids = set(patients["patient_id"].dropna())
        renal_ids = set(renal["patient_id"].dropna())
        clinical_ids = set(clinical["patient_id"].dropna())
        # Canonical identity checks are deliberately non-mutating: identifiers are
        # inspected after trimming/case-folding, but source values are never rewritten.
        id_series = {
            "patients": patients["patient_id"],
            "renal": renal["patient_id"],
            "clinical": clinical["patient_id"],
        }
        normalized_ids = {name: values.astype("string").str.strip().str.casefold()
                          for name, values in id_series.items()}
        invalid_id_counts = {
            name: int((values.isna() | values.str.strip().eq("")).sum())
            for name, values in id_series.items()
        }
        padded_id_counts = {
            name: int((values.notna() & values.astype("string").ne(values.astype("string").str.strip())).sum())
            for name, values in id_series.items()
        }
        normalized_patient_ids = normalized_ids["patients"].dropna()
        normalized_patient_collisions = int(normalized_patient_ids.duplicated().sum())
        normalized_patient_set = set(normalized_patient_ids)
        normalized_renal_set = set(normalized_ids["renal"].dropna())
        normalized_clinical_set = set(normalized_ids["clinical"].dropna())
        # Parse as UTC to make mixed-offset inputs deterministic; compare calendar dates
        # after normalization so timestamps on the same day cannot evade duplicate checks.
        dates = pd.to_datetime(renal["measurement_date"], errors="coerce", utc=True, format="mixed")
        calendar_dates = dates.dt.strftime("%Y-%m-%d")
        egfr = pd.to_numeric(renal["egfr_ml_min_1_73m2"], errors="coerce")
        creat = pd.to_numeric(renal["creatinine_mg_dl"], errors="coerce")
        seq = pd.to_numeric(renal["measurement_sequence"], errors="coerce")
        age = pd.to_numeric(patients["age_years"], errors="coerce")
        bmi = pd.to_numeric(clinical["bmi_simulated"], errors="coerce")
        checks.extend([
            {"check":"unique_patient_ids","passed":patients.patient_id.notna().all() and patients.patient_id.is_unique,
             "null_patient_ids":int(patients.patient_id.isna().sum()),"duplicate_patient_ids":int(patients.patient_id.duplicated().sum())},
            {"check":"unique_patient_calendar_day_measurements","passed":not pd.DataFrame({"patient_id":renal["patient_id"],"calendar_date":calendar_dates}).duplicated().any(),
             "duplicate_measurements":int(pd.DataFrame({"patient_id":renal["patient_id"],"calendar_date":calendar_dates}).duplicated().sum()),
             "description":"Máximo una medición renal por paciente y día calendario"},
            {"check":"unique_clinical_patient_rows","passed":clinical.patient_id.notna().all() and clinical.patient_id.is_unique,
             "duplicate_rows":int(clinical.patient_id.duplicated().sum())},
            {"check":"renal_patient_references","passed":renal_ids.issubset(pids),"orphan_patient_ids":len(renal_ids-pids)},
            {"check":"clinical_patient_references","passed":clinical_ids.issubset(pids),"orphan_patient_ids":len(clinical_ids-pids)},
            {"check":"patient_identifier_integrity","passed":all(v == 0 for v in invalid_id_counts.values()) and all(v == 0 for v in padded_id_counts.values()) and normalized_patient_collisions == 0,
             "invalid_or_blank_ids":invalid_id_counts,"whitespace_padded_ids":padded_id_counts,
             "normalized_patient_id_collisions":normalized_patient_collisions,
             "description":"Los identificadores deben ser no vacíos, no contener espacios externos y ser únicos tras normalización."},
            {"check":"renal_foreign_key_integrity","passed":renal["patient_id"].notna().all() and renal_ids.issubset(pids),
             "null_foreign_keys":int(renal["patient_id"].isna().sum()),
             "orphan_or_mismatched_patient_ids":len(renal_ids-pids),
             "description":"La clave foránea debe coincidir exactamente con el identificador maestro."},
            {"check":"clinical_foreign_key_integrity","passed":clinical["patient_id"].notna().all() and clinical_ids.issubset(pids),
             "null_foreign_keys":int(clinical["patient_id"].isna().sum()),
             "orphan_or_mismatched_patient_ids":len(clinical_ids-pids),
             "description":"La clave foránea debe coincidir exactamente con el identificador maestro."},
            {"check":"clinical_patient_coverage","passed":clinical_ids == pids,
             "patients_without_clinical_row":len(pids-clinical_ids),
             "clinical_ids_without_patient":len(clinical_ids-pids),
             "description":"En el conjunto sintético de demostración se espera una fila clínica por paciente."},
            {"check":"renal_patient_coverage","passed":renal_ids == pids,
             "patients_without_renal_measurements":len(pids-renal_ids),
             "renal_ids_without_patient":len(renal_ids-pids),
             "description":"En el conjunto sintético de demostración se espera al menos una medición renal por paciente."},
            {"check":"valid_measurement_dates","passed":dates.notna().all(),"invalid_dates":int(dates.isna().sum())},
            {"check":"finite_numeric_values","passed":all(np.isfinite(values.dropna()).all() for values in [egfr,creat,seq,age,bmi]),
             "non_finite_counts":{name:int((~np.isfinite(values.dropna())).sum()) for name,values in [("egfr",egfr),("creatinine",creat),("sequence",seq),("age",age),("bmi",bmi)]}},
            {"check":"no_future_measurements_vs_reference_date","passed":True if reference_date is None else bool((dates.dropna().dt.normalize() <= pd.Timestamp(reference_date, tz="UTC").normalize()).all()),
             "reference_date":None if reference_date is None else str(reference_date),
             "future_measurements":0 if reference_date is None else int((dates.dropna().dt.normalize() > pd.Timestamp(reference_date, tz="UTC").normalize()).sum()),
             "note":"Solo se aplica cuando se proporciona explícitamente una fecha de referencia; no se infiere una fecha de corte."},
            {"check":"valid_egfr_values","passed":egfr.dropna().between(0,200).all(),"missing_egfr_allowed":int(egfr.isna().sum()),
             "out_of_range":int((~egfr.dropna().between(0,200)).sum())},
            {"check":"positive_creatinine","passed":creat.notna().all() and creat.gt(0).all(),"missing_or_nonpositive":int((creat.isna()|creat.le(0)).sum())},
            {"check":"age_demo_range","passed":age.notna().all() and age.between(18,110).all(),"invalid_age":int((age.isna()|~age.between(18,110)).sum())},
            {"check":"bmi_demo_range","passed":bmi.notna().all() and bmi.between(10,80).all(),"invalid_bmi":int((bmi.isna()|~bmi.between(10,80)).sum())},
            {"check":"valid_measurement_sequence","passed":seq.notna().all() and seq.ge(1).all() and np.isfinite(seq.dropna()).all() and np.equal(seq.dropna(), np.floor(seq.dropna())).all(),"invalid_sequence":int((seq.isna()|seq.lt(1)|~np.isfinite(seq)|((seq % 1) != 0)).sum())},
            {"check":"unique_sequence_per_patient","passed":not renal.assign(_seq=seq).duplicated(["patient_id","_seq"]).any(),"duplicate_patient_sequences":int(renal.assign(_seq=seq).duplicated(["patient_id","_seq"]).sum())},
            {"check":"sequence_matches_chronology","passed":all(
                group.assign(_date=dates.loc[group.index], _seq=seq.loc[group.index]).sort_values("_date")["_seq"].is_monotonic_increasing
                for _, group in renal.groupby("patient_id", sort=False)
            ),"description":"La secuencia no debe retroceder al ordenar por fecha"},
            {"check":"contiguous_patient_sequence","passed":all(
                sorted_values == list(range(1, len(sorted_values) + 1))
                for sorted_values in renal.assign(_seq=seq).groupby("patient_id", sort=False)["_seq"].apply(lambda values: sorted(values.dropna().astype(float).tolist()))
            ),"description":"Cada paciente debe tener secuencias enteras consecutivas desde 1"},
            {"check":"chronological_patient_records","passed":all(
                dates.loc[idx].is_monotonic_increasing
                for _, idx in renal.groupby("patient_id", sort=False).groups.items()
            )},
            {"check":"measurement_dates_not_null_after_normalization","passed":calendar_dates.notna().all(),
             "invalid_normalized_dates":int(calendar_dates.isna().sum())},
            {"check":"synthetic_identifier_prefix","passed":patients.patient_id.astype(str).str.startswith("SYN-").all()
             and renal.patient_id.astype(str).str.startswith("SYN-").all()
             and clinical.patient_id.astype(str).str.startswith("SYN-").all()}
        ])
    passed = sum(bool(c["passed"]) for c in checks)
    return {
        "dataset_type":"SYNTHETIC_ONLY", "clinical_use":False,
        "checks_passed":passed, "checks_total":len(checks),
        "all_checks_passed":all(c["passed"] for c in checks),
        "row_counts":{"patients":len(patients),"renal_measurements":len(renal),"clinical_variables":len(clinical)},
        "checks":checks,
        "limitations":[
            "Controles técnicos de demostración; no son umbrales clínicos.",
            "Los escenarios sintéticos no representan prevalencia ni historia natural.",
            "Los valores faltantes de TFG son admisibles para probar escenarios incompletos; no se imputan en esta validación.",
            "No se calcula diagnóstico ni rendimiento predictivo.",
            "La ausencia de alertas técnicas no demuestra validez clínica."
        ]
    }
