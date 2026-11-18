"""Provenance-aware exports for the synthetic demonstration dashboard."""
from __future__ import annotations
import json
from typing import Any
import pandas as pd

class DemoExportError(ValueError):
    """Raised when a synthetic demo export cannot be safely produced."""

DISCLAIMER="DATOS 100 % SINTETICOS. NO CONTIENE INFORMACION DE PACIENTES REALES. NO ES UN DISPOSITIVO MEDICO NI UNA HERRAMIENTA DE DIAGNOSTICO."

def build_export_metadata(version: str, artifact_type: str, row_count: int) -> dict[str, Any]:
    version=str(version).strip().removeprefix('v')
    artifact_type=str(artifact_type).strip()
    if not version or any(ch not in '0123456789.' for ch in version): raise DemoExportError('Versión de exportación inválida')
    if not artifact_type or len(artifact_type)>80 or any(ord(ch)<32 for ch in artifact_type): raise DemoExportError('Tipo de artefacto inválido')
    if isinstance(row_count,bool) or not isinstance(row_count,int) or row_count<0: raise DemoExportError('El conteo de filas debe ser un entero no negativo')
    return {'product':'PALIC Renal Intelligence','release_version':version,'artifact_type':artifact_type,'row_count':row_count,'data_classification':'SYNTHETIC_ONLY','clinical_use':False,'predictive_model_connected':False,'disclaimer':DISCLAIMER}

def csv_export_with_provenance(frame: pd.DataFrame, version: str, artifact_type: str) -> bytes:
    if not isinstance(frame, pd.DataFrame):
        raise DemoExportError('La exportación requiere una tabla')
    if frame.columns.duplicated().any():
        raise DemoExportError('No se permiten columnas duplicadas')
    if len(frame.columns) == 0:
        raise DemoExportError('No se exportan tablas sin columnas')
    metadata = build_export_metadata(version, artifact_type, len(frame))
    comment = '# ' + json.dumps(metadata, ensure_ascii=False, separators=(',', ':')) + chr(10)
    try:
        safe_frame = frame.copy()
        # Neutralize spreadsheet formula injection in textual cells while
        # preserving numeric negatives as numeric values.
        for column in safe_frame.select_dtypes(include=["object", "string"]).columns:
            safe_frame[column] = safe_frame[column].map(
                lambda value: ("'" + value) if isinstance(value, str)
                and value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")) else value
            )
        csv_text = safe_frame.to_csv(index=False, lineterminator=chr(10))
        return ('\ufeff' + comment + csv_text).encode('utf-8')
    except (TypeError, ValueError, UnicodeError) as exc:
        raise DemoExportError('No fue posible serializar la exportación sintética') from exc

def json_export_with_provenance(payload: dict[str,Any], version: str, artifact_type: str) -> bytes:
    if not isinstance(payload,dict): raise DemoExportError('La exportación JSON requiere un objeto')
    metadata=build_export_metadata(version,artifact_type,len(payload))
    envelope={'metadata':metadata,'data':payload}
    try: return json.dumps(envelope,ensure_ascii=False,indent=2,allow_nan=False).encode('utf-8')
    except (TypeError,ValueError) as exc: raise DemoExportError('JSON inválido o con valores no finitos') from exc

def empty_state_message(subject: str, available_rows: int) -> str:
    if isinstance(available_rows,bool) or not isinstance(available_rows,int) or available_rows<0: raise DemoExportError('Conteo de registros inválido')
    clean=str(subject).strip()
    if not clean or len(clean)>100: raise DemoExportError('Etiqueta de estado vacío inválida')
    return f'No hay registros disponibles para {clean}.' if available_rows==0 else f'Hay {available_rows} registros disponibles para {clean}.'
