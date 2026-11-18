"""Build the complete SHA-256 inventory for PALIC Renal Intelligence v1.0.0."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "RELEASE_MANIFEST.json"
IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    inventory = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST:
            continue
        rel = path.relative_to(ROOT)
        if any(part in IGNORED_DIRS for part in rel.parts) or path.suffix.lower() in IGNORED_SUFFIXES:
            continue
        if path.is_symlink():
            raise SystemExit(f"No se admiten enlaces simbólicos en el paquete: {rel}")
        inventory[rel.as_posix()] = digest(path)
    payload = {
        "product": "PALIC Renal Intelligence",
        "version": "1.0.0",
        "release_type": "final_candidate_for_competition_submission",
        "data_policy": "SYNTHETIC_ONLY",
        "clinical_use": False,
        "predictive_model_connected": False,
        "predictor_contract_count": 28,
        "random_seed": 20261105,
        "adversarial_audits": 10,
        "release_note": "Liberación v1.0.0 con diez auditorías adversariales; revisar AUDIT_REPORT_V1.0.0.md y TEN_ADVERSARIAL_AUDITS.md.",
        "file_inventory_count": len(inventory),
        "file_sha256": inventory,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Manifiesto creado: {len(inventory)} archivos")


if __name__ == "__main__":
    main()
