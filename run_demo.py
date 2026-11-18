import argparse
import json
import shutil
import tempfile
from pathlib import Path

from src.environment.check import require_environment
from src.synthetic_data.generator import generate_synthetic_data
from src.data_quality.validation import validate_datasets
from src.longitudinal_engine.engine import build_longitudinal_dataset
from src.longitudinal_engine.traceability import validate_landmark_traceability
from src.longitudinal_engine.aggregate_audit import reconcile_aggregate_outputs
from src.io_safety.safe_io import (
    publish_directory_transactionally,
    read_csv_checked, read_json_checked,
)


def main():
    parser = argparse.ArgumentParser(description="Genera una demo longitudinal sintética de forma transaccional.")
    parser.add_argument('--patients', type=int, default=500)
    parser.add_argument('--seed', type=int, default=20261105)
    parser.add_argument('--out', default='data/generated')
    args = parser.parse_args()
    if args.patients < 10:
        parser.error('--patients debe ser >= 10')
    if args.seed < 0:
        parser.error('--seed debe ser un entero no negativo')

    require_environment(Path(__file__).resolve().parent, profile='core')
    destination = Path(args.out).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f'.{destination.name}.staging-', dir=destination.parent))
    try:
        patients, renal, clinical = generate_synthetic_data(args.patients, args.seed)
        quality = validate_datasets(patients, renal, clinical)
        if not quality.get('all_checks_passed', False):
            raise RuntimeError('La validación de calidad no aprobó; no se publicarán resultados parciales.')

        longitudinal, audit = build_longitudinal_dataset(renal)
        audit['seed'] = args.seed
        audit['generator_version'] = 'v1.0.0'
        traceability = validate_landmark_traceability(renal, longitudinal)
        audit['traceability'] = traceability
        reconciliation = reconcile_aggregate_outputs(
            patients, renal, clinical, longitudinal, quality, audit
        )
        audit['aggregate_reconciliation'] = reconciliation
        if not traceability.get('all_checks_passed', False):
            raise RuntimeError('La trazabilidad longitudinal no aprobó; no se publicarán resultados parciales.')
        if not reconciliation.get('all_checks_passed', False):
            raise RuntimeError('La conciliación agregada no aprobó; no se publicarán resultados parciales.')

        patients.to_csv(staging / 'patients_synthetic.csv', index=False)
        renal.to_csv(staging / 'renal_measurements_synthetic.csv', index=False)
        clinical.to_csv(staging / 'clinical_variables_synthetic.csv', index=False)
        longitudinal.to_csv(staging / 'longitudinal_landmarks_synthetic.csv', index=False)
        (staging / 'quality_report.json').write_text(
            json.dumps(quality, indent=2, ensure_ascii=False,
                       default=lambda x: x.item() if hasattr(x, 'item') else str(x)), encoding='utf-8')
        (staging / 'longitudinal_audit.json').write_text(
            json.dumps(audit, indent=2, ensure_ascii=False,
                       default=lambda x: x.item() if hasattr(x, 'item') else str(x)), encoding='utf-8')

        # Read-after-write checks: never publish a partial or malformed artifact set.
        read_csv_checked(staging / 'patients_synthetic.csv', required_columns=['patient_id', 'age_years', 'sex', 'region', 'scenario'])
        read_csv_checked(staging / 'renal_measurements_synthetic.csv', required_columns=['patient_id', 'measurement_date', 'egfr_ml_min_1_73m2', 'measurement_sequence'])
        read_csv_checked(staging / 'clinical_variables_synthetic.csv', required_columns=['patient_id', 'hypertension_simulated', 'diabetes_simulated', 'bmi_simulated'])
        read_csv_checked(staging / 'longitudinal_landmarks_synthetic.csv', required_columns=['patient_id', 'index_date', 'evaluable_365', 'target_sustained_40'])
        read_json_checked(staging / 'quality_report.json')
        read_json_checked(staging / 'longitudinal_audit.json')

        publish_directory_transactionally(staging, destination)
        print('Synthetic patients:', len(patients))
        print('Renal measurements:', len(renal))
        print('Quality:', quality['checks_passed'], '/', quality['checks_total'])
        print('Landmarks:', audit['landmarks'])
        print('Evaluable:', audit['evaluable_365'])
        print('Non-evaluable:', audit['non_evaluable_365'])
        print('Raw events:', audit['events_raw'])
        print('Traceability:', traceability['checks_passed'], '/', traceability['checks_total'])
        print('Aggregate reconciliation:', reconciliation['checks_passed'], '/', reconciliation['checks_total'])
        print('Output:', destination)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


if __name__ == '__main__':
    main()
