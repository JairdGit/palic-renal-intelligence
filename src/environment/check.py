"""Offline, fail-closed runtime dependency and Python compatibility checks."""
from __future__ import annotations

import importlib.metadata
import json
import platform
import re
import sys
from pathlib import Path

from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion


class EnvironmentCheckError(RuntimeError):
    pass


def _read_requirements(path: str | Path) -> list[Requirement]:
    path = Path(path)
    if not path.is_file():
        raise EnvironmentCheckError(f"No existe el archivo de dependencias: {path}")
    requirements: list[Requirement] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r ", "--", "-e ")):
            raise EnvironmentCheckError(f"Directiva no admitida en requirements, línea {number}: {line}")
        try:
            requirements.append(Requirement(line))
        except Exception as exc:
            raise EnvironmentCheckError(f"Dependencia inválida en línea {number}: {line}") from exc
    return requirements


def check_environment(root: str | Path, *, profile: str = "core", python_version=None,
                      installed_versions=None) -> dict:
    """Check Python >=3.10,<3.14 and profile-specific offline requirements.

    core: pandas/numpy; app: requirements-app.txt when present;
    model: optional research dependencies from requirements-model.txt.
    """
    if profile not in {"core", "app", "model"}:
        raise ValueError("profile debe ser 'core', 'app' o 'model'")
    root = Path(root)
    current = Version(str(python_version or platform.python_version()))
    python_ok = Version("3.10") <= current < Version("3.14")
    if profile == "app" and (root / "requirements-app.txt").is_file():
        requirements = _read_requirements(root / "requirements-app.txt")
    elif profile == "model" and (root / "requirements-model.txt").is_file():
        requirements = _read_requirements(root / "requirements-model.txt")
    else:
        requirements = _read_requirements(root / "requirements.txt")
    if profile == "core":
        requirements = [r for r in requirements if r.name.lower() in {"pandas", "numpy"}]
    simulated_environment = installed_versions is not None
    installed_versions = installed_versions if simulated_environment else {}
    checks = []
    failures = []
    for requirement in requirements:
        name = requirement.name
        if simulated_environment:
            # A supplied mapping is authoritative: omitted keys mean absent packages.
            installed = installed_versions.get(name)
        else:
            try:
                installed = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                installed = None
        valid = installed is not None
        if valid:
            try:
                valid = (not requirement.specifier) or Version(installed) in requirement.specifier
            except InvalidVersion:
                valid = False
        item = {"name": name, "required": str(requirement.specifier) or "any",
                "installed": installed, "passed": bool(valid)}
        checks.append(item)
        if not valid:
            failures.append(item)
    report = {
        "profile": profile,
        "python": {"version": str(current), "required": ">=3.10,<3.14", "passed": python_ok},
        "dependency_checks": checks,
        "checks_passed": sum(1 for item in checks if item["passed"]),
        "checks_total": len(checks),
        "failures": failures,
        "all_checks_passed": python_ok and not failures,
    }
    return report


def require_environment(root: str | Path, *, profile: str = "core") -> dict:
    report = check_environment(root, profile=profile)
    if not report["all_checks_passed"]:
        details = "; ".join(
            f"{item['name']}: requerido {item['required']}, instalado {item['installed']}"
            for item in report["failures"]
        )
        if not report["python"]["passed"]:
            details = (details + "; " if details else "") + (
                f"Python {report['python']['version']} fuera del rango >=3.10,<3.14")
        raise EnvironmentCheckError(f"Entorno incompatible ({profile}). {details}")
    return report


def write_environment_report(report: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
