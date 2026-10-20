from pathlib import Path
from datetime import datetime
import shutil

BATCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BATCH_ROOT.parent
TARGET = PROJECT_ROOT / 'backend' / 'app' / 'providers' / 'aadwik_character_quality.py'
SOURCE = BATCH_ROOT / 'app' / 'repair' / 'aadwik_character_quality.py'


def main():
    print('AADWIK Batch 30 Phase 23 character API restore')
    print(f'Project root: {PROJECT_ROOT}')
    print(f'Source: {SOURCE}')
    print(f'Live target: {TARGET}')
    if not SOURCE.exists():
        print('ERROR: Batch 30 source not found.')
        return 2
    if not TARGET.parent.exists():
        print('ERROR: Live providers directory not found.')
        return 2
    if TARGET.exists():
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = TARGET.with_name(f'aadwik_character_quality.backup_v30_{stamp}.py')
        shutil.copy2(TARGET, backup)
        print(f'Backup: {backup}')
    shutil.copy2(SOURCE, TARGET)
    print('Phase 23 character-quality implementation restored.')
    print('Required legacy builders restored: build_tara, build_guardian, build_shadow, build_blue_star.')
    print('Blender and FFmpeg were not modified.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
