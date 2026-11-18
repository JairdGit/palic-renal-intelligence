"""Deterministic, safe guided route through the six demo dashboard sections."""
from __future__ import annotations

from typing import Any


class DemoJourneyError(ValueError):
    """Raised when a demo journey selection or route is invalid."""


DEMO_STEPS = (
    {
        "section": "Resumen",
        "purpose": "Presentar el tamaño y la composición del conjunto sintético.",
        "action": "Revisar pacientes, mediciones, landmarks, evaluabilidad y escenarios.",
        "message": "Los escenarios fueron diseñados para probar comportamientos de software; no representan prevalencia poblacional.",
        "duration_minutes": 2,
    },
    {
        "section": "Trayectorias",
        "purpose": "Mostrar cómo se organiza temporalmente la TFG de un paciente sintético.",
        "action": "Seleccionar un identificador SYN-, revisar la serie y localizar el landmark.",
        "message": "Las curvas y estadísticas son descriptivas y no constituyen diagnóstico ni predicción.",
        "duration_minutes": 3,
    },
    {
        "section": "Auditoría por paciente",
        "purpose": "Explicar la regla computacional del desenlace longitudinal.",
        "action": "Inspeccionar evaluabilidad, observaciones futuras y estado del desenlace.",
        "message": "Un registro no evaluable conserva el objetivo nulo; no se recodifica como ausencia de evento.",
        "duration_minutes": 3,
    },
    {
        "section": "Inteligencia de riesgo",
        "purpose": "Distinguir la referencia documental de investigación de una inferencia conectada.",
        "action": "Mostrar el contrato de 28 predictores y las métricas históricas con sus límites.",
        "message": "El modelo predictivo real está desconectado; no se generan probabilidades individuales ni categorías de riesgo.",
        "duration_minutes": 2,
    },
    {
        "section": "Calidad de datos",
        "purpose": "Exponer controles de calidad, conciliación y disponibilidad de artefactos.",
        "action": "Revisar los controles, el estado operativo y los patrones de frecuencia.",
        "message": "Los controles aprobados demuestran consistencia técnica dentro del alcance probado, no validez clínica.",
        "duration_minutes": 3,
    },
    {
        "section": "Trazabilidad",
        "purpose": "Cerrar con las reglas, configuración y límites de la demostración.",
        "action": "Repasar versión, semilla, horizonte, evaluabilidad y exclusiones.",
        "message": "Esta es una demo técnica sintética; no es un dispositivo médico ni una herramienta asistencial.",
        "duration_minutes": 2,
    },
)


def build_demo_journey() -> dict[str, Any]:
    """Return the canonical route in navigation order."""
    steps = [dict(step, order=index + 1) for index, step in enumerate(DEMO_STEPS)]
    return {
        "steps": steps,
        "sections": [step["section"] for step in steps],
        "total_minutes": sum(step["duration_minutes"] for step in steps),
        "synthetic_only": True,
        "predictive_model_connected": False,
    }


def get_demo_step(section: str) -> dict[str, Any]:
    """Resolve a section to its immutable-by-copy guided instruction."""
    if not isinstance(section, str) or not section.strip():
        raise DemoJourneyError("La sección debe ser un texto no vacío")
    for index, step in enumerate(DEMO_STEPS, start=1):
        if section == step["section"]:
            return dict(step, order=index)
    raise DemoJourneyError("La sección no pertenece al recorrido oficial de demostración")


def validate_demo_navigation(sections: list[str]) -> dict[str, Any]:
    """Fail closed unless the six dashboard sections appear once in canonical order."""
    if not isinstance(sections, list) or any(not isinstance(x, str) for x in sections):
        raise DemoJourneyError("La navegación debe ser una lista de secciones de texto")
    expected = [step["section"] for step in DEMO_STEPS]
    duplicates = len(sections) != len(set(sections))
    unknown = [item for item in sections if item not in expected]
    missing = [item for item in expected if item not in sections]
    ordered = sections == expected
    return {
        "valid": ordered and not duplicates and not unknown and not missing,
        "ordered": ordered,
        "duplicates": duplicates,
        "unknown": unknown,
        "missing": missing,
        "expected": expected,
    }
