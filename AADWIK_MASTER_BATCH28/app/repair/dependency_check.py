from pathlib import Path
import importlib.util


def source_exists(path):
    return Path(path).is_file()


def module_importable(path):
    path = Path(path)
    if not path.is_file():
        return False
    spec = importlib.util.spec_from_file_location("aadwik_character_quality", path)
    if spec is None or spec.loader is None:
        return False
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return True
    except Exception:
        return False
