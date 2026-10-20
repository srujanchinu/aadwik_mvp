from pathlib import Path
from datetime import datetime
import shutil

from .live_backend_contract import target_is_compatible, integration_block, MARKER


def install(target: str | Path) -> tuple[bool, str]:
    path = Path(target)
    if not path.exists():
        return False, "target_not_found"

    text = path.read_text(encoding="utf-8")
    if not target_is_compatible(text):
        return False, "unexpected_target_shape"

    if MARKER in text:
        return True, "already_installed"

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(f"{path.stem}.backup_v26_{stamp}{path.suffix}")
    shutil.copy2(path, backup)

    try:
        path.write_text(text.rstrip() + integration_block(), encoding="utf-8")
    except Exception:
        shutil.copy2(backup, path)
        return False, "write_failed_restored"

    return True, str(backup)
