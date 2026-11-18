import unittest
import pandas as pd
from src.synthetic_data.generator import generate_synthetic_data
from src.longitudinal_engine.engine import build_longitudinal_dataset
from src.longitudinal_engine.traceability import validate_landmark_traceability


class LandmarkTraceabilityV085(unittest.TestCase):
    def setUp(self):
        _, self.renal, _ = generate_synthetic_data(100, 20261105)
        self.landmarks, _ = build_longitudinal_dataset(self.renal)

    def report(self, output=None):
        return validate_landmark_traceability(self.renal, self.landmarks if output is None else output)

    def test_generated_output_has_complete_traceability(self):
        report = self.report()
        self.assertTrue(report['all_checks_passed'], report)
        self.assertEqual(report['checks_total'], 10)

    def test_duplicate_landmark_is_rejected(self):
        altered = pd.concat([self.landmarks, self.landmarks.iloc[[0]]], ignore_index=True)
        check = next(c for c in self.report(altered)['checks'] if c['check'] == 'one_landmark_per_patient')
        self.assertFalse(check['passed'])

    def test_orphan_landmark_is_rejected(self):
        altered = self.landmarks.copy()
        altered.loc[0, 'patient_id'] = 'SYN-ORPHAN'
        check = next(c for c in self.report(altered)['checks'] if c['check'] == 'source_output_patient_coverage')
        self.assertFalse(check['passed'])

    def test_missing_landmark_is_rejected(self):
        altered = self.landmarks.iloc[1:].copy()
        check = next(c for c in self.report(altered)['checks'] if c['check'] == 'source_output_patient_coverage')
        self.assertFalse(check['passed'])

    def test_index_value_must_exist_in_source(self):
        altered = self.landmarks.copy()
        altered.loc[0, 'index_egfr'] += 0.25
        check = next(c for c in self.report(altered)['checks'] if c['check'] == 'index_record_lineage')
        self.assertFalse(check['passed'])

    def test_future_count_must_match_source(self):
        altered = self.landmarks.copy()
        altered.loc[0, 'future_valid_tfg_count'] += 1
        check = next(c for c in self.report(altered)['checks'] if c['check'] == 'future_observation_count')
        self.assertFalse(check['passed'])

    def test_last_future_date_must_match_source(self):
        altered = self.landmarks.copy()
        altered.loc[0, 'last_future_date'] = '2099-01-01'
        check = next(c for c in self.report(altered)['checks'] if c['check'] == 'last_future_date')
        self.assertFalse(check['passed'])

    def test_censored_target_must_remain_missing(self):
        altered = self.landmarks.copy()
        idx = altered.index[~altered['evaluable_365']][0]
        altered.loc[idx, 'target_sustained_40'] = 0.0
        check = next(c for c in self.report(altered)['checks'] if c['check'] == 'censoring_target_policy')
        self.assertFalse(check['passed'])

    def test_event_confirmation_must_be_within_horizon(self):
        altered = self.landmarks.copy()
        idxs = altered.index[altered['target_sustained_40_raw'] == 1]
        if len(idxs):
            altered.loc[idxs[0], 'confirmation_date'] = pd.to_datetime(altered.loc[idxs[0], 'index_date']) + pd.Timedelta(days=366)
            check = next(c for c in self.report(altered)['checks'] if c['check'] == 'event_temporal_bounds')
            self.assertFalse(check['passed'])
        else:
            self.skipTest('Synthetic sample has no confirmed events')

    def test_missing_required_column_fails_closed(self):
        altered = self.landmarks.drop(columns=['index_date'])
        report = self.report(altered)
        self.assertFalse(report['all_checks_passed'])
        self.assertEqual(report['checks'][0]['check'], 'required_columns')


if __name__ == '__main__':
    unittest.main()
