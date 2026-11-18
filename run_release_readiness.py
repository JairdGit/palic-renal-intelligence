"""Run static release-readiness checks for PALIC Renal Intelligence v1.0.0."""
from pathlib import Path
import json
from src.release.readiness import build_release_readiness

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    result = build_release_readiness(ROOT)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "READY_FOR_FINAL_REVIEW" else 2)
