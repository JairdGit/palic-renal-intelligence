from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: se esperaba 1 coincidencia y se encontraron {count}")
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aplica correcciones de reproducibilidad a PALIC Renal Intelligence v1.0.0"
    )
    parser.add_argument("root", nargs="?", default=".", help="Carpeta raíz del proyecto")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    targets = {
        "environment": root / "src" / "environment" / "check.py",
        "patient_test": root / "tests" / "test_adversarial_v093.py",
        "preflight_test": root / "tests" / "test_adversarial_v089.py",
        "app": root / "app.py",
    }
    missing = [str(path) for path in targets.values() if not path.is_file()]
    if missing:
        raise SystemExit("No se encontraron estos archivos:\n" + "\n".join(missing))

    # An explicitly supplied mapping is a complete simulated environment.
    p = targets["environment"]
    text = p.read_text(encoding="utf-8")
    old = '''    installed_versions = installed_versions or {}
    checks = []
'''
    new = '''    simulated_environment = installed_versions is not None
    installed_versions = installed_versions if simulated_environment else {}
    checks = []
'''
    text = replace_once(text, old, new, "check.py: distinguir entorno simulado")
    old = '''        try:
            installed = installed_versions.get(name) or importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            installed = None
'''
    new = '''        if simulated_environment:
            # A supplied mapping is authoritative: omitted keys mean absent packages.
            installed = installed_versions.get(name)
        else:
            try:
                installed = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                installed = None
'''
    text = replace_once(text, old, new, "check.py: resolver dependencias")
    p.write_text(text, encoding="utf-8")

    # Keep invalid date as object data so the tested function receives it.
    p = targets["patient_test"]
    text = p.read_text(encoding="utf-8")
    old = '''        broken = self.renal.copy()
        idx = broken.index[broken.patient_id.astype(str).eq(selected)][0]
        broken.loc[idx, "measurement_date"] = "invalid-date"
'''
    new = '''        broken = self.renal.copy()
        broken["measurement_date"] = broken["measurement_date"].astype("object")
        idx = broken.index[broken.patient_id.astype(str).eq(selected)][0]
        broken.loc[idx, "measurement_date"] = "invalid-date"
'''
    text = replace_once(text, old, new, "test_adversarial_v093.py: fixture de fecha")
    p.write_text(text, encoding="utf-8")

    # Simulate missing Streamlit in a subprocess, independent of local packages.
    p = targets["preflight_test"]
    text = p.read_text(encoding="utf-8")
    old = '''        result = subprocess.run([sys.executable, str(ROOT / "app.py")], cwd=ROOT,
                                text=True, capture_output=True, timeout=30)
'''
    new = '''        bootstrap = (
            "import importlib.metadata as md, runpy, sys; "
            "original = md.version; "
            "md.version = lambda name: (_ for _ in ()).throw(md.PackageNotFoundError(name)) "
            "if name.lower() == 'streamlit' else original(name); "
            "runpy.run_path(sys.argv[1], run_name='__main__')"
        )
        result = subprocess.run(
            [sys.executable, "-c", bootstrap, str(ROOT / "app.py")],
            cwd=ROOT, text=True, capture_output=True, timeout=30,
        )
'''
    text = replace_once(text, old, new, "test_adversarial_v089.py: preflight aislado")
    p.write_text(text, encoding="utf-8")

    # Migrate deprecated Streamlit width argument.
    p = targets["app"]
    text = p.read_text(encoding="utf-8")
    count = text.count("use_container_width=True")
    if count < 1:
        raise RuntimeError("app.py: no se encontraron usos de use_container_width=True")
    text = text.replace("use_container_width=True", 'width="stretch"')
    if "use_container_width=" in text:
        raise RuntimeError("app.py: quedaron usos de use_container_width")
    p.write_text(text, encoding="utf-8")

    print("CORRECCIONES APLICADAS")
    print("- check.py: entorno simulado aislado")
    print("- test_adversarial_v093.py: fixture de fecha compatible con Pandas")
    print("- test_adversarial_v089.py: preflight independiente del entorno real")
    print(f"- app.py: {count} usos migrados a width='stretch'")
    print("No se modificaron RELEASE_MANIFEST.json ni los datos generados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
