from pathlib import Path
from datetime import datetime
import shutil


MODULE_NAME = "aadwik_character_quality.py"


def install_dependency(source, backend_providers):
    source = Path(source)
    backend_providers = Path(backend_providers)

    if not source.is_file():
        return False, "source_not_found"

    backend_providers.mkdir(parents=True, exist_ok=True)
    target = backend_providers / MODULE_NAME

    backup = None
    if target.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = target.with_name(
            f"aadwik_character_quality.backup_v28_{stamp}.py"
        )
        shutil.copy2(target, backup)

    shutil.copy2(source, target)
    return True, str(backup) if backup else "installed"


def target_path(backend_root):
    return Path(backend_root) / "app" / "providers" / MODULE_NAME
