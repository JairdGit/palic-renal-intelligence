from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

DEFAULT_CONTRACT = Path(__file__).resolve().parents[2] / "models" / "research_reference" / "effective_predictors.json"

def load_predictor_contract(path: str | Path = DEFAULT_CONTRACT, family: str = "full_clinical") -> list[str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if family not in payload:
        raise KeyError(f"Familia de predictores no encontrada: {family}")
    features = payload[family]
    if not isinstance(features, list) or not features or len(features) != len(set(features)):
        raise ValueError("Contrato de predictores inválido: lista vacía o duplicada.")
    return features

def align_features(frame: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    missing = [name for name in features if name not in frame.columns]
    if missing:
        raise ValueError(f"Faltan predictores requeridos ({len(missing)}): {missing}")
    aligned = frame.loc[:, features].copy()
    if list(aligned.columns) != features:
        raise AssertionError("No se pudo conservar el orden canónico de predictores.")
    return aligned

def validate_model_feature_count(model, expected_count: int):
    actual = getattr(model, "n_features_in_", None)
    if actual is None and hasattr(model, "named_steps"):
        last = list(model.named_steps.values())[-1]
        actual = getattr(last, "n_features_in_", None)
    if actual is not None and int(actual) != int(expected_count):
        raise ValueError(f"El modelo espera {actual} variables; el contrato declara {expected_count}.")
    return actual
