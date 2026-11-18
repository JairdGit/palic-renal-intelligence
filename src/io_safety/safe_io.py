"""Fail-closed input validation and transactional publication for demo artifacts."""
from __future__ import annotations

import json
import csv
import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterable

import pandas as pd


class ArtifactReadError(ValueError):
    """Raised when a required artifact is missing, malformed, or structurally invalid."""


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ArtifactReadError(f"Clave JSON duplicada: {key}")
        result[key] = value
    return result


def read_json_checked(path: str | Path, *, expected_type=dict):
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ArtifactReadError(f"No se pudo leer JSON requerido '{path.name}': {exc}") from exc
    try:
        value = json.loads(raw, object_pairs_hook=_reject_duplicate_keys,
                           parse_constant=lambda token: (_ for _ in ()).throw(
                               ArtifactReadError(f"Constante JSON no finita: {token}")))
    except (json.JSONDecodeError, ArtifactReadError) as exc:
        raise ArtifactReadError(f"JSON inválido en '{path.name}': {exc}") from exc
    if not isinstance(value, expected_type):
        raise ArtifactReadError(
            f"Estructura inválida en '{path.name}': se esperaba {expected_type.__name__}"
        )
    return value


def read_csv_checked(path: str | Path, *, required_columns: Iterable[str],
                     date_columns: Iterable[str] = ()) -> pd.DataFrame:
    path = Path(path)
    try:
        if not path.is_file():
            raise ArtifactReadError(f"Falta el archivo requerido '{path.name}'")
        if path.stat().st_size == 0:
            raise ArtifactReadError(f"El archivo '{path.name}' está vacío")
        # pandas silently renames duplicate CSV headers (e.g. x, x -> x, x.1).
        # Inspect the raw header first so ambiguous schemas fail closed.
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            header = next(csv.reader(stream), None)
        if not header or any(not str(name).strip() for name in header):
            raise ArtifactReadError(f"El CSV '{path.name}' tiene encabezado vacío o inválido")
        if len(header) != len(set(header)):
            raise ArtifactReadError(f"El CSV '{path.name}' contiene encabezados duplicados")
        frame = pd.read_csv(path, on_bad_lines="error", encoding="utf-8")
    except ArtifactReadError:
        raise
    except (OSError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise ArtifactReadError(f"CSV inválido en '{path.name}': {exc}") from exc
    missing = sorted(set(required_columns) - set(frame.columns))
    if missing:
        raise ArtifactReadError(f"Columnas requeridas ausentes en '{path.name}': {missing}")
    if frame.empty:
        raise ArtifactReadError(f"El CSV '{path.name}' no contiene registros")
    for column in date_columns:
        parsed = pd.to_datetime(frame[column], errors="coerce")
        invalid = parsed.isna() & frame[column].notna()
        if invalid.any() or parsed.isna().any():
            raise ArtifactReadError(
                f"Fechas inválidas o vacías en '{path.name}', columna '{column}'"
            )
        frame[column] = parsed
    return frame


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def publish_directory_transactionally(staging: str | Path, destination: str | Path) -> None:
    """Replace a complete output directory; restore prior output if promotion fails."""
    staging = Path(staging).resolve()
    destination = Path(destination).resolve()
    if not staging.is_dir():
        raise ValueError("El directorio temporal de publicación no existe")
    if staging.parent != destination.parent:
        raise ValueError("La publicación debe ocurrir en el mismo directorio padre")
    backup = destination.with_name(destination.name + ".previous")
    if backup.exists():
        shutil.rmtree(backup) if backup.is_dir() else backup.unlink()
    moved_old = False
    try:
        if destination.exists():
            os.replace(destination, backup)
            moved_old = True
        os.replace(staging, destination)
    except Exception:
        if destination.exists() and destination != staging:
            shutil.rmtree(destination, ignore_errors=True)
        if moved_old and backup.exists():
            os.replace(backup, destination)
        raise
    else:
        if backup.exists():
            shutil.rmtree(backup) if backup.is_dir() else backup.unlink()


def atomic_write_json(path: str | Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False,
                      default=lambda x: x.item() if hasattr(x, "item") else str(x))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
