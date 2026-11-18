"""Run the reproducible acceptance checklist for the synthetic dashboard demo."""
from pathlib import Path
import json

from src.dashboard.demo_acceptance import build_demo_acceptance
from src.dashboard.demo_journey import build_demo_journey
from src.dashboard.diagnostics import build_operational_diagnostics
from src.dashboard.validation import validate_dashboard_data
from src.integrity.manifest import verify_release_manifest
from src.io_safety.safe_io import read_csv_checked, read_json_checked

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "generated"


def main() -> int:
    integrity = verify_release_manifest(ROOT, strict=True, expected_version="1.0.0")
    patients = read_csv_checked(DATA / "patients_synthetic.csv", required_columns=["patient_id", "age_years", "sex", "region", "scenario"])
    renal = read_csv_checked(DATA / "renal_measurements_synthetic.csv", required_columns=["patient_id", "measurement_date", "egfr_ml_min_1_73m2", "measurement_sequence"], date_columns=["measurement_date"])
    clinical = read_csv_checked(DATA / "clinical_variables_synthetic.csv", required_columns=["patient_id", "hypertension_simulated", "diabetes_simulated", "bmi_simulated"])
    landmarks = read_csv_checked(DATA / "longitudinal_landmarks_synthetic.csv", required_columns=["patient_id", "index_date", "evaluable_365", "target_sustained_40"], date_columns=["index_date"])
    read_json_checked(DATA / "quality_report.json")
    read_json_checked(DATA / "longitudinal_audit.json")
    contract = validate_dashboard_data(patients, renal, clinical, landmarks)
    operational = build_operational_diagnostics(ROOT, integrity)
    acceptance = build_demo_acceptance(root=ROOT, integrity=integrity, operational=operational,
                                       data_contract=contract, journey=build_demo_journey())
    print(json.dumps(acceptance, indent=2, ensure_ascii=False))
    return 0 if acceptance["status"] == "READY_FOR_GUIDED_DEMO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
