import tempfile
import unittest
from pathlib import Path

from app.repair.dependency_check import source_exists, module_importable
from app.repair.live_dependency import install_dependency, target_path


class TestMasterBatch28(unittest.TestCase):
    def test_dependency_source_exists(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "aadwik_character_quality.py"
            source.write_text("VALUE = 23\n", encoding="utf-8")
            self.assertTrue(source_exists(source))

    def test_dependency_module_is_importable(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "aadwik_character_quality.py"
            source.write_text("VALUE = 23\n", encoding="utf-8")
            self.assertTrue(module_importable(source))

    def test_live_target_path(self):
        path = target_path(r"C:\aadwik\backend")
        self.assertTrue(str(path).endswith(
            r"backend\app\providers\aadwik_character_quality.py"
        ))

    def test_install_copies_dependency(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "source.py"
            source.write_text("VALUE = 23\n", encoding="utf-8")
            providers = Path(td) / "providers"
            ok, info = install_dependency(source, providers)
            self.assertTrue(ok)
            self.assertEqual(info, "installed")
            self.assertTrue((providers / "aadwik_character_quality.py").exists())

    def test_install_backs_up_existing_dependency(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "source.py"
            source.write_text("NEW = True\n", encoding="utf-8")
            providers = Path(td) / "providers"
            providers.mkdir()
            target = providers / "aadwik_character_quality.py"
            target.write_text("OLD = True\n", encoding="utf-8")

            ok, info = install_dependency(source, providers)
            self.assertTrue(ok)
            self.assertNotEqual(info, "installed")
            self.assertTrue(Path(info).exists())
            self.assertIn("NEW", target.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
