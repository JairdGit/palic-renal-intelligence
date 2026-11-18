import unittest
from src.synthetic_data.generator import generate_synthetic_data
from src.data_quality.validation import validate_datasets
from src.longitudinal_engine.engine import select_landmarks,build_longitudinal_dataset,summarize_trajectory
from src.longitudinal_engine.outcome_audit import audit_patient_outcome

class EngineTests(unittest.TestCase):
 def test_seed_reproducibility(self):
  a=generate_synthetic_data(50,123); b=generate_synthetic_data(50,123); self.assertTrue(a[1].equals(b[1]))
 def test_quality(self):
  p,r,c=generate_synthetic_data(100,123); self.assertTrue(validate_datasets(p,r,c)['all_checks_passed'])
 def test_landmark_contract(self):
  _,r,_=generate_synthetic_data(100,123); lm,a=select_landmarks(r); self.assertTrue(lm.patient_id.is_unique); self.assertTrue((lm.index_date<=a['cutoff_date']).all()); self.assertFalse(a['uses_future_for_index_selection'])
 def test_trajectory_summary(self):
  _,r,_=generate_synthetic_data(30,321)
  h=r[r.patient_id==r.patient_id.iloc[0]]
  summary=summarize_trajectory(h)
  self.assertGreaterEqual(summary['n_measurements'],1)
  self.assertIn('absolute_change',summary)
 def test_patient_outcome_audit_agrees_with_engine(self):
  _,r,_=generate_synthetic_data(100,20261105)
  out,_=build_longitudinal_dataset(r)
  row=out.loc[out.target_sustained_40==1].iloc[0]
  audit=audit_patient_outcome(r,row)
  self.assertEqual(audit['status'],'EVENT_CONFIRMED')
  self.assertGreaterEqual(audit['confirmation_gap_days'],30)
 def test_censoring_and_output(self):
  _,r,_=generate_synthetic_data(100,123); out,a=build_longitudinal_dataset(r); self.assertTrue((out.loc[~out.evaluable_365,'target_sustained_40'].isna()).all()); self.assertEqual(len(out),a['landmarks'])
if __name__=='__main__': unittest.main()
