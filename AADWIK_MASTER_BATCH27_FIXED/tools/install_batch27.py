from pathlib import Path
from datetime import datetime
import shutil
import sys

# This file lives at:
# <project>\AADWIK_MASTER_BATCH27\tools\install_batch27.py
# Therefore parents[2] is the actual project root.
BATCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BATCH_ROOT.parent
TARGET = PROJECT_ROOT / "backend" / "app" / "api" / "movies.py"
INTEGRATION_DIR = PROJECT_ROOT / "backend" / "app" / "integration"
SOURCE = BATCH_ROOT / "app" / "integration" / "live_runtime.py"

sys.path.insert(0, str(BATCH_ROOT))
from app.integration.live_patch import patch_text, already_patched


def main():
    print("AADWIK Batch 27 installer")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target: {TARGET}")

    if not TARGET.exists():
        print("ERROR: movies.py not found. No changes made.")
        return 2

    text = TARGET.read_text(encoding="utf-8")

    if already_patched(text):
        print("Batch 27 already installed. No changes made.")
        return 0

    try:
        patched = patch_text(text)
    except Exception as exc:
        print(f"ERROR: {exc}. No changes made.")
        return 3

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = TARGET.with_name(
        f"{TARGET.stem}.backup_v27_{stamp}{TARGET.suffix}"
    )

    INTEGRATION_DIR.mkdir(parents=True, exist_ok=True)

    if not SOURCE.exists():
        print("ERROR: Batch 27 integration source is missing. No changes made.")
        return 5

    shutil.copy2(TARGET, backup)
    integration_target = INTEGRATION_DIR / "live_runtime.py"
    shutil.copy2(SOURCE, integration_target)

    try:
        TARGET.write_text(patched, encoding="utf-8")
    except Exception as exc:
        shutil.copy2(backup, TARGET)
        print(f"ERROR: write failed ({exc}); original restored.")
        return 4

    print(f"Backup: {backup}")
    print(f"Integration module: {integration_target}")
    print("Batch 27 hook installed.")
    print("MASTER_RUNTIME_ENABLED remains False.")
    print("Existing generation flow remains active.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
