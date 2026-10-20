from pathlib import Path
import sys

BATCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BATCH_ROOT.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
TARGET_DIR = BACKEND_ROOT / "app" / "providers"
SOURCE = BATCH_ROOT / "app" / "repair" / "character_quality_source.py"

sys.path.insert(0, str(BATCH_ROOT))
from app.repair.character_dependency import install_character_dependency


def main():
    print("AADWIK Batch 29 character dependency repair")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Source: {SOURCE}")
    print(f"Live target: {TARGET_DIR / 'aadwik_character_quality.py'}")

    ok, result = install_character_dependency(SOURCE, TARGET_DIR)
    if not ok:
        print(f"ERROR: {result}")
        return 2

    print(f"Dependency installed: {result}")
    print("movies.py was not modified.")
    print("Blender and FFmpeg were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
