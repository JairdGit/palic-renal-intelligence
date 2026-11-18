import unittest
import pandas as pd
import numpy as np
from src.data_quality.validation import validate_datasets

class TemporalValidationV083(unittest.TestCase):
    def setUp(self):
        self.p = pd.DataFrame([{"patient_id":"SYN-001","age_years":50,"sex":"F","region":"X","scenario":"stable"}])
        self.r = pd.DataFrame([
            {"patient_id":"SYN-001","measurement_date":"2024-01-01","egfr_ml_min_1_73m2":90,"creatinine_mg_dl":1.0,"measurement_sequence":1},
            {"patient_id":"SYN-001","measurement_date":"2024-03-01","egfr_ml_min_1_73m2":88,"creatinine_mg_dl":1.1,"measurement_sequence":2},
        ])
        self.c = pd.DataFrame([{"patient_id":"SYN-001","hypertension_simulated":0,"diabetes_simulated":0,"bmi_simulated":24}])
    def check(self, name):
        report=validate_datasets(self.p,self.r,self.c)
        return next(x for x in report['checks'] if x['check']==name)
    def test_duplicate_same_calendar_day_with_different_time_detected(self):
        self.r.loc[1,'measurement_date']='2024-01-01T18:00:00Z'
        self.assertFalse(self.check('unique_patient_calendar_day_measurements')['passed'])
    def test_invalid_date_detected(self):
        self.r.loc[0,'measurement_date']='not-a-date'
        self.assertFalse(self.check('valid_measurement_dates')['passed'])
    def test_nan_or_infinity_numeric_guard(self):
        self.r['egfr_ml_min_1_73m2']=self.r['egfr_ml_min_1_73m2'].astype(float)
        self.r.loc[0,'egfr_ml_min_1_73m2']=np.inf
        self.assertFalse(self.check('finite_numeric_values')['passed'])
    def test_reference_date_future_guard_only_when_explicit(self):
        report=validate_datasets(self.p,self.r,self.c,reference_date='2024-02-01')
        check=next(x for x in report['checks'] if x['check']=='no_future_measurements_vs_reference_date')
        self.assertFalse(check['passed'])
    def test_no_inferred_reference_date(self):
        self.assertTrue(self.check('no_future_measurements_vs_reference_date')['passed'])
    def test_unsorted_rows_detected(self):
        self.r=self.r.iloc[::-1].reset_index(drop=True)
        self.assertFalse(self.check('chronological_patient_records')['passed'])
    def test_mixed_timezone_dates_parse(self):
        self.r.loc[0,'measurement_date']='2024-01-01T00:00:00-05:00'
        self.assertTrue(self.check('valid_measurement_dates')['passed'])

if __name__=='__main__': unittest.main()
