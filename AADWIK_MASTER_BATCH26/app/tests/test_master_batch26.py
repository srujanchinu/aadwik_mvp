import tempfile
import unittest
from pathlib import Path

from app.integration.live_backend_contract import (
    MARKER, LiveIntegrationContract, target_is_compatible, integration_block
)
from app.integration.live_backend_state import LiveBackendState
from app.integration.live_backend_installer import install
from app.integration.live_backend_dispatch import LiveBackendDispatcher


def handler(**kwargs):
    return {"accepted": True, "movie_id": kwargs["movie_id"]}


class TestMasterBatch26(unittest.TestCase):
    def test_contract_target_validation(self):
        self.assertTrue(target_is_compatible(
            "from fastapi import APIRouter\nrouter=APIRouter()\n# /movies"
        ))
        self.assertFalse(target_is_compatible("print('x')"))
        self.assertTrue(LiveIntegrationContract().preserve_existing_generation)

    def test_integration_block_contains_marker(self):
        self.assertIn(MARKER, integration_block())

    def test_state_progress(self):
        state = LiveBackendState("movie-26-001", "pipeline-26-001")
        state.update("running", 55)
        self.assertEqual(state.status, "running")
        self.assertEqual(state.progress, 55)

    def test_dispatch_is_safe_when_disabled_and_works_when_enabled(self):
        disabled = LiveBackendDispatcher(handler)
        self.assertFalse(disabled.dispatch("m1", "p1")["accepted"])

        enabled = LiveBackendDispatcher(handler, enabled=True)
        result = enabled.dispatch("m2", "p2")
        self.assertTrue(result["accepted"])

    def test_installer_creates_backup_and_marker(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "movies.py"
            target.write_text(
                "from fastapi import APIRouter\nrouter=APIRouter()\n# /movies\n",
                encoding="utf-8"
            )
            ok, info = install(target)
            self.assertTrue(ok)
            self.assertTrue(Path(info).exists())
            self.assertIn(MARKER, target.read_text(encoding="utf-8"))

            ok2, info2 = install(target)
            self.assertTrue(ok2)
            self.assertEqual(info2, "already_installed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
