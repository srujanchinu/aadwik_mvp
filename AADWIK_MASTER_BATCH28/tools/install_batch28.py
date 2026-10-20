from pathlib import Path
import sys

BATCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BATCH_ROOT.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
TARGET = BACKEND_ROOT / "app" / "providers" / "aadwik_character_quality.py"

# Prefer the known Phase 23 package if it exists in the project.
CANDIDATES = [
    PROJECT_ROOT / "AADWIK_PHASE23_CHARACTER_CINEMATIC_UPGRADE" / "providers" / "aadwik_character_quality.py",
    PROJECT_ROOT / "AADWIK_MASTER_BATCH23" / "providers" / "aadwik_character_quality.py",
]

sys.path.insert(0, str(BATCH_ROOT))
from app.repair.live_dependency import install_dependency


def main():
    print("AADWIK Batch 28 dependency repair")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Live target: {TARGET}")

    source = next((p for p in CANDIDATES if p.is_file()), None)
    if source is None:
        print("ERROR: Phase 23 aadwik_character_quality.py source not found.")
        print("Checked:")
        for candidate in CANDIDATES:
            print(f" - {candidate}")
        return 2

    print(f"Source: {source}")
    ok, info = install_dependency(source, TARGET.parent)

    if not ok:
        print(f"ERROR: {info}")
        return 3

    if info == "installed":
        print("Dependency installed.")
    else:
        print(f"Existing dependency backed up: {info}")
        print("Dependency replaced with Phase 23 version.")

    print("Blender import dependency repaired.")
    print("movies.py was not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
