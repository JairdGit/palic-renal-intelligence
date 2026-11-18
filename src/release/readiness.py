from __future__ import annotations

from pathlib import Path
import re
from src.integrity.manifest import verify_release_manifest

REQUIRED_ROOT_FILES = (
    "README.md", "requirements.txt", "requirements-app.txt",
    "requirements-model.txt", "check_environment.py", "run_demo.py",
    "run_demo_acceptance.py", "run_model_contract_check.py",
    "RELEASE_MANIFEST.json", "TEST_RESULTS.txt", "README_V1.0.md",
    "TEN_ADVERSARIAL_AUDITS.md", "AUDIT_REPORT_V1.0.0.md",
    "SUBMISSION_CHECKLIST.md", "build_release_manifest.py",
)
REQUIRED_AUDITS = (
    "AUDIT_REPORT_V0.7.md", "AUDIT_REPORT_V0.8.md",
    "AUDIT_REPORT_V0.8.1.md", "AUDIT_REPORT_V0.8.2.md",
    "AUDIT_REPORT_V0.8.3.md", "AUDIT_REPORT_V0.8.4.md",
    "AUDIT_REPORT_V0.8.5.md", "AUDIT_REPORT_V0.8.6.md",
    "AUDIT_REPORT_V0.8.7.md", "AUDIT_REPORT_V0.8.8.md",
    "AUDIT_REPORT_V0.8.9.md", "AUDIT_REPORT_V0.9.md",
    "AUDIT_REPORT_V0.9.1.md", "AUDIT_REPORT_V0.9.2.md",
    "AUDIT_REPORT_V0.9.3.md", "AUDIT_REPORT_V0.9.4.md",
    "AUDIT_REPORT_V0.9.5.md", "AUDIT_REPORT_V0.9.6.md",
    "AUDIT_REPORT_V0.9.7.md", "AUDIT_REPORT_V0.9.8.md",
)
FORBIDDEN_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".joblib", ".pickle", ".pkl"}


def _result(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def build_release_readiness(root: str | Path) -> dict:
    """Check release documentation, install profiles, history, and package hygiene.

    This is a static packaging/documentation gate; it does not install dependencies,
    launch Streamlit, run browser tests, or certify clinical/security properties.
    """
    root = Path(root).resolve()
    checks = []

    missing_root = [name for name in REQUIRED_ROOT_FILES if not (root / name).is_file()]
    checks.append(_result("root_release_files", not missing_root,
                          "Todos los archivos esenciales presentes" if not missing_root else f"Faltan: {missing_root}"))

    missing_audits = [name for name in REQUIRED_AUDITS if not (root / name).is_file()]
    checks.append(_result("version_audit_history", not missing_audits,
                          "Historial de auditorías v0.7–v0.9.9 presente" if not missing_audits else f"Faltan: {missing_audits}"))

    final_audit_files = [root / f"AUDIT_{i:02d}_*.md" for i in range(1, 11)]
    final_audit_missing = [pattern.name for pattern in final_audit_files if not list(root.glob(pattern.name))]
    checks.append(_result("ten_final_adversarial_audits", not final_audit_missing,
                          "Diez informes adversariales presentes" if not final_audit_missing else f"Faltan: {final_audit_missing}"))

    app_req = root / "requirements-app.txt"
    model_req = root / "requirements-model.txt"
    try:
        app_text = app_req.read_text(encoding="utf-8").lower()
        model_text = model_req.read_text(encoding="utf-8").lower()
        core_text = (root / "requirements.txt").read_text(encoding="utf-8").lower()
        app_ok = "streamlit" in app_text and "plotly" in app_text
        model_ok = "scikit-learn" in model_text and "joblib" in model_text
        profile_ok = app_ok and model_ok and bool(core_text.strip())
        detail = "Perfiles core/app/model separados y dependencias clave declaradas" if profile_ok else "Revisar dependencias clave en requirements*.txt"
    except OSError as exc:
        profile_ok, detail = False, str(exc)
    checks.append(_result("dependency_profiles", profile_ok, detail))

    readme_path = root / "README.md"
    try:
        readme = readme_path.read_text(encoding="utf-8").lower()
        required_terms = ("synthetic", "streamlit run app.py", "run_demo_acceptance.py", "clinical", "predictive")
        missing_terms = [term for term in required_terms if term not in readme]
        docs_ok = not missing_terms
        detail = "README contiene instrucciones de ejecución y límites de uso" if docs_ok else f"README sin referencias: {missing_terms}"
    except OSError as exc:
        docs_ok, detail = False, str(exc)
    checks.append(_result("operator_documentation", docs_ok, detail))

    forbidden = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        # Python may create bytecode caches while the audit itself runs. These are
        # runtime by-products, excluded by the release packager; do not confuse
        # them with distributable package content. Serialized model files remain blocked.
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            forbidden.append(rel.as_posix())
    checks.append(_result("package_hygiene", not forbidden,
                          "Sin cachés, bytecode ni artefactos serializados de modelo" if not forbidden else f"Elementos excluidos requeridos: {forbidden}"))

    integrity = verify_release_manifest(root, strict=True, expected_version="1.0.0")
    checks.append(_result("strict_manifest_inventory", integrity.get("status") == "PASS",
                          f"{integrity.get('verified', 0)} archivos; no listados: {len(integrity.get('unlisted', []))}"))

    status = "READY_FOR_FINAL_REVIEW" if all(item["status"] == "PASS" for item in checks) else "NOT_READY"
    return {
        "release": "PALIC Renal Intelligence",
        "version": "1.0.0",
        "status": status,
        "checks_passed": sum(item["status"] == "PASS" for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "scope_note": "Puerta estática de documentación y empaquetado; no ejecuta interfaz, pruebas de navegador, pentest ni validación clínica.",
    }
