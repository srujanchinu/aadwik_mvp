from pathlib import Path
from datetime import datetime
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "backend" / "app" / "api" / "movies.py"

# Import local batch modules without requiring package installation.
sys.path.insert(0, str(ROOT))
from app.integration.movies_wiring import validate_target_text
from app.integration.wiring_marker import has_marker, marker_block


def main():
    print("AADWIK Batch 24 live wiring installer")
    print(f"Target: {TARGET}")

    if not TARGET.exists():
        print("ERROR: target movies.py was not found.")
        return 2

    text = TARGET.read_text(encoding="utf-8")

    if not validate_target_text(text):
        print("ERROR: target does not match expected FastAPI movies router shape.")
        print("No changes made.")
        return 3

    if has_marker(text):
        print("Already wired: marker exists. No changes made.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = TARGET.with_name(f"{TARGET.stem}.backup_v24_{stamp}{TARGET.suffix}")
    shutil.copy2(TARGET, backup)

    try:
        TARGET.write_text(text.rstrip() + marker_block(), encoding="utf-8")
    except Exception:
        shutil.copy2(backup, TARGET)
        print("ERROR: write failed; original file restored from backup.")
        return 4

    print(f"Backup created: {backup}")
    print("Live wiring marker installed.")
    print("NOTE: this batch does not enable or replace the existing generation runner.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
