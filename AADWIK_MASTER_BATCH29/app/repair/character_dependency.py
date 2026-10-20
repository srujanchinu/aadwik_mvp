from pathlib import Path
from datetime import datetime
import shutil

MODULE_NAME = "aadwik_character_quality.py"


def required_symbols():
    return ("build_character", "apply_emotion", "direct_character_gaze")


def validate_module_text(text):
    return all(f"def {name}" in text for name in required_symbols())


def install_character_dependency(source, target_dir):
    source = Path(source)
    target_dir = Path(target_dir)
    if not source.is_file():
        return False, "source_not_found"
    text = source.read_text(encoding="utf-8")
    if not validate_module_text(text):
        return False, "required_symbols_missing"

    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / MODULE_NAME
    if target.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = target.with_name(f"aadwik_character_quality.backup_v29_{stamp}.py")
        shutil.copy2(target, backup)

    shutil.copy2(source, target)
    return True, str(target)
