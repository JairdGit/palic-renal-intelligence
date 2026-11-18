import argparse
import json
from pathlib import Path

from src.environment.check import check_environment


def main():
    parser = argparse.ArgumentParser(description="Verifica perfiles core, app o model sin instalar paquetes ni acceder a internet.")
    parser.add_argument("--profile", choices=["core", "app", "model"], default="core")
    args = parser.parse_args()
    report = check_environment(Path(__file__).resolve().parent, profile=args.profile)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["all_checks_passed"] else 2)


if __name__ == "__main__":
    main()
