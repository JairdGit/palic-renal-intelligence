import unittest
import pandas as pd
import tempfile
from pathlib import Path
from src.model_integration.contract import load_predictor_contract, align_features, validate_model_feature_count
from src.model_integration.loader import load_trusted_joblib

class DummyModel:
    n_features_in_ = 28

class ModelIntegrationTests(unittest.TestCase):
    def test_contract_has_28_effective_predictors(self):
        features = load_predictor_contract()
        self.assertEqual(len(features), 28)
        self.assertEqual(len(features), len(set(features)))

    def test_alignment_preserves_exact_order(self):
        features = load_predictor_contract()
        frame = pd.DataFrame([{f: 1 for f in reversed(features)}])
        aligned = align_features(frame, features)
        self.assertEqual(list(aligned.columns), features)

    def test_missing_feature_fails_closed(self):
        features = load_predictor_contract()
        frame = pd.DataFrame([{f: 1 for f in features[:-1]}])
        with self.assertRaises(ValueError):
            align_features(frame, features)

    def test_model_feature_count(self):
        self.assertEqual(validate_model_feature_count(DummyModel(), 28), 28)

    def test_joblib_loading_fails_closed_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "placeholder.joblib"
            artifact.write_bytes(b"not-a-real-model")
            with self.assertRaises(PermissionError):
                load_trusted_joblib(artifact)

if __name__ == "__main__":
    unittest.main()
