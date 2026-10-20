import unittest

from app.integration.runtime_bridge import MasterRuntimeBridge
from app.integration.runtime_status import validate_transition, normalize_runtime_status
from app.integration.runtime_config import RuntimeConfig, production_config
from app.integration.backend_entrypoint import make_entrypoint


def runner(**kwargs):
    return {"accepted": True, "movie_id": kwargs["movie_id"]}


class TestMasterBatch25(unittest.TestCase):
    def test_bridge_disabled_by_default(self):
        bridge = MasterRuntimeBridge()
        job = bridge.create_job("movie-25-001", "A story")
        result = bridge.dispatch(job)
        self.assertFalse(result.accepted)
        self.assertEqual(result.status, "bypassed")

    def test_enabled_bridge_dispatches(self):
        bridge = MasterRuntimeBridge(enabled=True, pipeline_runner=runner)
        job = bridge.create_job("movie-25-002", "A story")
        result = bridge.dispatch(job)
        self.assertTrue(result.accepted)
        self.assertEqual(result.status, "dispatched")

    def test_terminal_status_cannot_regress(self):
        self.assertTrue(validate_transition("running", "completed"))
        with self.assertRaises(ValueError):
            validate_transition("completed", "running")

    def test_runtime_status_is_normalized(self):
        result = normalize_runtime_status("verifying", 70)
        self.assertEqual(result["status"], "verifying")
        self.assertEqual(result["progress"], 70)

    def test_config_and_entrypoint(self):
        config = production_config()
        self.assertTrue(config.enabled)
        self.assertFalse(config.dry_run)
        ep = make_entrypoint("movie_runner", lambda **kw: kw["movie_id"])
        self.assertEqual(ep.call(movie_id="movie-25-005"), "movie-25-005")


if __name__ == "__main__":
    unittest.main(verbosity=2)
