import unittest
import pandas as pd
import numpy as np
from src.dashboard.visualization import (DashboardVisualizationError, build_trajectory_chart_data, build_outcome_annotation, build_observation_status_counts)

class DashboardVisualizationV094(unittest.TestCase):
    def setUp(self):
        self.renal=pd.DataFrame({'measurement_date':pd.to_datetime(['2024-03-01','2024-01-01','2024-02-01']),'egfr_ml_min_1_73m2':[55.,70.,60.]})
        self.landmark=pd.DataFrame([{'index_date':pd.Timestamp('2024-01-01'),'index_egfr':70.,'evaluable_365':1,'target_sustained_40':0,'observation_status':'EVALUABLE'}])
    def test_trajectory_is_sorted_and_days_relative(self):
        out=build_trajectory_chart_data(self.renal,self.landmark)
        self.assertTrue(out.measurement_date.is_monotonic_increasing)
        self.assertEqual(out.days_from_first_measurement.tolist(),[0.,31.,60.])
    def test_landmark_and_threshold_are_explicit(self):
        out=build_trajectory_chart_data(self.renal,self.landmark)
        self.assertEqual(out.loc[out.point_role.eq('landmark'),'measurement_date'].iloc[0],pd.Timestamp('2024-01-01'))
        self.assertTrue((out.threshold_60pct==42.).all())
    def test_all_points_are_marked_synthetic(self):
        self.assertTrue(build_trajectory_chart_data(self.renal).synthetic_data.all())
    def test_invalid_date_rejected(self):
        broken=self.renal.copy(); broken['measurement_date']=broken.measurement_date.astype(str); broken.loc[0,'measurement_date']='bad'
        with self.assertRaises(DashboardVisualizationError): build_trajectory_chart_data(broken)
    def test_nonfinite_egfr_rejected(self):
        broken=self.renal.copy(); broken.loc[0,'egfr_ml_min_1_73m2']=np.inf
        with self.assertRaises(DashboardVisualizationError): build_trajectory_chart_data(broken)
    def test_duplicate_date_rejected(self):
        broken=pd.concat([self.renal,self.renal.iloc[[0]]],ignore_index=True)
        with self.assertRaises(DashboardVisualizationError): build_trajectory_chart_data(broken)
    def test_multiple_landmarks_rejected(self):
        with self.assertRaises(DashboardVisualizationError): build_trajectory_chart_data(self.renal,pd.concat([self.landmark,self.landmark]))
    def test_censored_outcome_keeps_null_target(self):
        row=self.landmark.copy(); row.loc[0,'evaluable_365']=0; row.loc[0,'target_sustained_40']=np.nan; row.loc[0,'observation_status']='CENSORED_NON_EVALUABLE'
        self.assertEqual(build_outcome_annotation(row)['display_label'],'No evaluable / censurado')
    def test_censored_nonnull_target_rejected(self):
        row=self.landmark.copy(); row.loc[0,'evaluable_365']=0; row.loc[0,'observation_status']='CENSORED_NON_EVALUABLE'
        with self.assertRaises(DashboardVisualizationError): build_outcome_annotation(row)
    def test_unknown_status_rejected(self):
        broken=pd.DataFrame({'observation_status':['OTHER']})
        with self.assertRaises(DashboardVisualizationError): build_observation_status_counts(broken)
    def test_status_counts_reconcile(self):
        frame=pd.DataFrame({'observation_status':['EVALUABLE','EVALUABLE','CENSORED_NON_EVALUABLE']})
        out=build_observation_status_counts(frame)
        self.assertEqual(out.Registros.sum(),3)
    def test_event_annotation_label(self):
        row=self.landmark.copy(); row.loc[0,'target_sustained_40']=1
        self.assertEqual(build_outcome_annotation(row)['display_label'],'Evento sintético confirmado')

ROOT=__import__('pathlib').Path(__file__).resolve().parents[1]
