import unittest
import pandas as pd
from src.synthetic_data.generator import generate_synthetic_data
from src.data_quality.validation import validate_datasets
from src.longitudinal_engine.engine import build_longitudinal_dataset
from src.longitudinal_engine.aggregate_audit import reconcile_aggregate_outputs


class AggregateReconciliationV086(unittest.TestCase):
    def setUp(self):
        self.patients, self.renal, self.clinical = generate_synthetic_data(100, 20261105)
        self.landmarks, self.audit = build_longitudinal_dataset(self.renal)
        self.quality = validate_datasets(self.patients, self.renal, self.clinical)

    def check(self, landmarks=None, quality=None, audit=None):
        return reconcile_aggregate_outputs(
            self.patients, self.renal, self.clinical,
            self.landmarks if landmarks is None else landmarks,
            self.quality if quality is None else quality,
            self.audit if audit is None else audit,
        )

    def test_baseline_aggregate_reconciliation_passes(self):
        report = self.check()
        self.assertTrue(report['all_checks_passed'], report)
        self.assertEqual(report['checks_total'], 12)

    def test_landmark_count_mismatch_is_detected(self):
        bad = dict(self.audit, landmarks=self.audit['landmarks'] + 1)
        self.assertFalse(self.check(audit=bad)['all_checks_passed'])

    def test_evaluable_denominator_mismatch_is_detected(self):
        bad = dict(self.audit, evaluable_365=self.audit['evaluable_365'] + 1)
        self.assertFalse(self.check(audit=bad)['all_checks_passed'])

    def test_raw_event_count_mismatch_is_detected(self):
        bad = dict(self.audit, events_raw=self.audit['events_raw'] + 1)
        self.assertFalse(self.check(audit=bad)['all_checks_passed'])

    def test_evaluable_event_count_mismatch_is_detected(self):
        bad = dict(self.audit, events_evaluable=self.audit['events_evaluable'] + 1)
        self.assertFalse(self.check(audit=bad)['all_checks_passed'])

    def test_quality_row_count_mismatch_is_detected(self):
        bad = dict(self.quality, row_counts=dict(self.quality['row_counts'], patients=999))
        self.assertFalse(self.check(quality=bad)['all_checks_passed'])

    def test_censored_patient_cannot_be_counted_as_no_event(self):
        bad = self.landmarks.copy()
        idx = bad.index[~bad.evaluable_365][0]
        bad.loc[idx, 'target_sustained_40'] = 0
        self.assertFalse(self.check(landmarks=bad)['all_checks_passed'])

    def test_evaluable_target_must_be_binary(self):
        bad = self.landmarks.copy()
        idx = bad.index[bad.evaluable_365][0]
        bad.loc[idx, 'target_sustained_40'] = 2
        self.assertFalse(self.check(landmarks=bad)['all_checks_passed'])

    def test_duplicate_landmark_breaks_reconciliation(self):
        bad = pd.concat([self.landmarks, self.landmarks.iloc[[0]]], ignore_index=True)
        self.assertFalse(self.check(landmarks=bad)['all_checks_passed'])

    def test_raw_and_evaluable_event_totals_must_reconcile(self):
        bad = self.landmarks.copy()
        idx = bad.index[(bad.evaluable_365) & (bad.target_sustained_40 == 0)][0]
        bad.loc[idx, 'target_sustained_40'] = 1
        self.assertFalse(self.check(landmarks=bad)['all_checks_passed'])


if __name__ == '__main__':
    unittest.main()
