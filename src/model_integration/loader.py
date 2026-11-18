from __future__ import annotations
from pathlib import Path
import warnings

def load_trusted_joblib(model_path: str | Path, *, allow_pickle: bool = False):
    """
    Load only a model artifact whose provenance and integrity have been verified.
    joblib/pickle deserialization can execute arbitrary code. It is disabled by default.
    """
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if not allow_pickle:
        raise PermissionError(
            "Carga bloqueada. Verifique procedencia, SHA-256 y entorno aislado; "
            "después habilite allow_pickle=True explícitamente."
        )
    warnings.warn(
        "Se va a deserializar un artefacto joblib. Hágalo solo si el archivo es de confianza "
        "y en un entorno aislado.",
        RuntimeWarning
    )
    import joblib
    return joblib.load(path)
