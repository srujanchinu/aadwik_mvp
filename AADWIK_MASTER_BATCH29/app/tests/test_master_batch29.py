import unittest
import tempfile
from pathlib import Path
import importlib.util

from app.repair.character_dependency import (
    required_symbols,
    validate_module_text,
    install_character_dependency,
)


class TestMasterBatch29(unittest.TestCase):
    def test_required_symbols(self):
        symbols = required_symbols()
        self.assertIn("build_character", symbols)
        self.assertIn("apply_emotion", symbols)
        self.assertIn("direct_character_gaze", symbols)

    def test_module_text_validation(self):
        text = "def build_character():\n" \
               "def apply_emotion():\n" \
               "def direct_character_gaze():\n"
        self.assertTrue(validate_module_text(text))
        self.assertFalse(validate_module_text("print('bad')"))

    def test_dependency_imports(self):
        source = Path(__file__).resolve().parents[2] / "app" / "repair" / "character_quality_source.py"
        spec = importlib.util.spec_from_file_location("character_quality_test", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.CHARACTERS["tara"].character_id, "char_tara_v2")

    def test_install_dependency(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "source.py"
            src.write_text(
                "def build_character(): pass\n"
                "def apply_emotion(): pass\n"
                "def direct_character_gaze(): pass\n",
                encoding="utf-8",
            )
            target_dir = Path(td) / "providers"
            ok, target = install_character_dependency(src, target_dir)
            self.assertTrue(ok)
            self.assertTrue(Path(target).exists())

    def test_installed_file_contains_required_symbols(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "source.py"
            src.write_text(
                "def build_character(): pass\n"
                "def apply_emotion(): pass\n"
                "def direct_character_gaze(): pass\n",
                encoding="utf-8",
            )
            target_dir = Path(td) / "providers"
            ok, target = install_character_dependency(src, target_dir)
            self.assertTrue(ok)
            self.assertTrue(validate_module_text(Path(target).read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
