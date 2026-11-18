"""Machine-verifiable acceptance checklist for the public synthetic demo."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from src.dashboard.demo_journey import build_demo_journey, validate_demo_navigation


class DemoAcceptanceError(ValueError):
    """Raised when demo acceptance inputs are malformed."""


REQUIRED_EXPORT_FUNCTIONS = (
    "csv_export_with_provenance",
    "json_export_with_provenance",
)
REQUIRED_DISCLOSURES = (
    "Datos 100 % sintéticos",
    "no diagnostica",
    "Modelo predictivo real no conectado",
)


def build_demo_acceptance(
    *,
    root: str | Path,
    integrity: dict[str, Any],
    operational: dict[str, Any],
    data_contract: dict[str, Any],
    journey: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate demo readiness without implying browser or clinical validation."""
    root_path = Path(root).resolve()
    if not isinstance(integrity, dict) or not isinstance(operational, dict):
        raise DemoAcceptanceError("Integridad y diagnóstico operativo deben ser objetos")
    if not isinstance(data_contract, dict):
        raise DemoAcceptanceError("El contrato de datos debe ser un objeto")
    journey = build_demo_journey() if journey is None else journey
    if not isinstance(journey, dict) or not isinstance(journey.get("sections"), list):
        raise DemoAcceptanceError("El recorrido de demostración tiene una estructura inválida")

    app_path = root_path / "app.py"
    exports_path = root_path / "src" / "dashboard" / "demo_exports.py"
    try:
        app_source = app_path.read_text(encoding="utf-8")
        exports_source = exports_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise DemoAcceptanceError(f"No se pudieron inspeccionar los componentes de demo: {exc}") from exc

    navigation = validate_demo_navigation(journey["sections"])
    route_ok = bool(navigation["valid"] and journey.get("total_minutes") == 15)
    disclosure_ok = all(text in app_source for text in REQUIRED_DISCLOSURES)
    export_ok = all(name in exports_source for name in REQUIRED_EXPORT_FUNCTIONS)
    checks = [
        {"name": "integridad_sha256", "passed": integrity.get("status") == "PASS",
         "detail": f"{integrity.get('verified', 0)} archivos verificados"},
        {"name": "artefactos_operativos", "passed": operational.get("status") == "OPERATIVO_DEMO",
         "detail": f"{operational.get('checks_passed', 0)}/{operational.get('checks_total', 0)} controles"},
        {"name": "contrato_datos_dashboard", "passed": data_contract.get("all_checks_passed") is True,
         "detail": f"{data_contract.get('checks_passed', 0)}/{data_contract.get('checks_total', 0)} controles"},
        {"name": "recorrido_seis_secciones_15_min", "passed": route_ok,
         "detail": f"{len(journey['sections'])} secciones; {journey.get('total_minutes')} minutos"},
        {"name": "declaraciones_de_seguridad_y_alcance", "passed": disclosure_ok,
         "detail": "Datos sintéticos, no diagnóstico y modelo desconectado"},
        {"name": "exportaciones_con_procedencia", "passed": export_ok,
         "detail": "CSV y JSON con metadatos de procedencia"},
    ]
    failed = [item["name"] for item in checks if not item["passed"]]
    return {
        "status": "READY_FOR_GUIDED_DEMO" if not failed else "NOT_READY",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failures": failed,
        "checks": checks,
        "browser_visual_test": "NOT_ASSESSED_BY_THIS_CHECKLIST",
        "clinical_validation": False,
        "predictive_model_connected": False,
        "scope": "Aceptación reproducible de artefactos, contrato de datos, recorrido y declaraciones de demo; no ejecuta navegador ni valida uso clínico.",
    }
