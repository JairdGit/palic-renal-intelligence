import unittest
import pandas as pd
from src.longitudinal_engine.outcome_audit import audit_patient_outcome

class AdversarialOutcomeTests(unittest.TestCase):
    def make_case(self, future_days, values, index_egfr=100.0):
        index_date = pd.Timestamp("2024-01-01")
        renal = pd.DataFrame({
            "patient_id": ["SYN-EDGE"] * (1 + len(future_days)),
            "measurement_date": [index_date] + [index_date + pd.Timedelta(days=d) for d in future_days],
            "egfr_ml_min_1_73m2": [index_egfr] + values
        })
        landmark = pd.Series({
            "patient_id": "SYN-EDGE",
            "index_date": index_date,
            "index_egfr": index_egfr
        })
        return audit_patient_outcome(renal, landmark)

    def test_confirmation_exactly_30_days_is_valid(self):
        result = self.make_case([10, 40], [50, 45])
        self.assertEqual(result["status"], "EVENT_CONFIRMED")
        self.assertEqual(result["confirmation_gap_days"], 30)

    def test_confirmation_at_29_days_is_not_valid(self):
        result = self.make_case([10, 39], [50, 45])
        self.assertEqual(result["status"], "CROSSING_NOT_CONFIRMED")

    def test_single_future_measurement_is_non_evaluable(self):
        result = self.make_case([100], [50])
        self.assertEqual(result["status"], "NON_EVALUABLE")
        self.assertEqual(result["future_valid_measurements"], 1)

    def test_no_threshold_crossing_is_evaluable_no_event(self):
        result = self.make_case([30, 90], [80, 75])
        self.assertEqual(result["status"], "EVALUABLE_NO_EVENT")

    def test_crossing_without_confirmation_is_not_event(self):
        result = self.make_case([30, 60], [50, 70])
        self.assertEqual(result["status"], "CROSSING_NOT_CONFIRMED")

    def test_day_365_is_included_and_day_366_excluded(self):
        result = self.make_case([100, 365, 366], [80, 50, 40])
        self.assertEqual(result["future_valid_measurements"], 2)
        self.assertEqual(result["status"], "CROSSING_NOT_CONFIRMED")

    def test_duplicate_same_day_does_not_create_30_day_confirmation(self):
        result = self.make_case([10, 10], [50, 40])
        self.assertEqual(result["status"], "CROSSING_NOT_CONFIRMED")

if __name__ == "__main__":
    unittest.main()
