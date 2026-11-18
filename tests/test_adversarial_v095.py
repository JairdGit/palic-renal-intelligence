import json, unittest
import numpy as np
import pandas as pd
from src.dashboard.demo_exports import (DemoExportError, build_export_metadata, csv_export_with_provenance, json_export_with_provenance, empty_state_message, DISCLAIMER)

class DemoExportHardeningV095(unittest.TestCase):
    def test_metadata_marks_synthetic_and_nonclinical(self):
        m=build_export_metadata('v0.9.5','patient_view',2)
        self.assertEqual(m['data_classification'],'SYNTHETIC_ONLY'); self.assertFalse(m['clinical_use']); self.assertFalse(m['predictive_model_connected'])
    def test_metadata_rejects_invalid_version(self):
        with self.assertRaises(DemoExportError): build_export_metadata('../1','x',0)
    def test_metadata_rejects_negative_rows(self):
        with self.assertRaises(DemoExportError): build_export_metadata('0.9.5','x',-1)
    def test_csv_contains_provenance_and_keeps_header(self):
        out=csv_export_with_provenance(pd.DataFrame({'patient_id':['SYN-1']}),'0.9.5','synthetic_patients').decode('utf-8-sig')
        self.assertTrue(out.startswith('# ')); self.assertIn('SYNTHETIC_ONLY',out); self.assertIn('patient_id',out)
    def test_csv_rejects_duplicate_columns(self):
        df=pd.DataFrame([[1,2]]); df.columns=['x','x']
        with self.assertRaises(DemoExportError): csv_export_with_provenance(df,'0.9.5','x')
    def test_csv_rejects_empty_schema(self):
        with self.assertRaises(DemoExportError): csv_export_with_provenance(pd.DataFrame(index=[0]),'0.9.5','x')
    def test_json_envelope_contains_metadata(self):
        obj=json.loads(json_export_with_provenance({'status':'ok'},'0.9.5','audit'))
        self.assertEqual(obj['metadata']['data_classification'],'SYNTHETIC_ONLY'); self.assertEqual(obj['data']['status'],'ok')
    def test_json_rejects_nan(self):
        with self.assertRaises(DemoExportError): json_export_with_provenance({'value':float('nan')},'0.9.5','audit')
    def test_empty_state_zero(self):
        self.assertIn('No hay registros',empty_state_message('la selección',0))
    def test_empty_state_nonzero(self):
        self.assertIn('3 registros',empty_state_message('la selección',3))
    def test_empty_state_rejects_negative(self):
        with self.assertRaises(DemoExportError): empty_state_message('x',-1)
    def test_disclaimer_is_explicit(self):
        self.assertIn('SINTETICOS',DISCLAIMER); self.assertIn('NO ES UN DISPOSITIVO MEDICO',DISCLAIMER)
