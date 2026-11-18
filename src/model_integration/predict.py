from __future__ import annotations
import pandas as pd
from .contract import load_predictor_contract, align_features, validate_model_feature_count

def predict_probabilities(model, feature_frame: pd.DataFrame, family: str = "full_clinical"):
    features = load_predictor_contract(family=family)
    X = align_features(feature_frame, features)
    validate_model_feature_count(model, len(features))
    if not hasattr(model, "predict_proba"):
        raise TypeError("El artefacto no expone predict_proba; revisar tipo de modelo.")
    probabilities = model.predict_proba(X)
    if getattr(probabilities, "ndim", 0) != 2 or probabilities.shape[1] < 2:
        raise ValueError("Salida predict_proba inesperada.")
    return pd.Series(probabilities[:, 1], index=feature_frame.index, name="risk_probability")
