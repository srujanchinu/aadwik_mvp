import unittest

from app.integration.production_adapter import ProductionBackendAdapter
from app.integration.backend_progress import from_pipeline_event
from app.integration.backend_result import normalize_backend_result
from app.integration.live_switch import ProductionIntegrationSwitch


def fake_backend(**kwargs):
    return {
        "success": True,
        "status": "completed",
        "artifact_path": "renders/movie-23.mp4",
        "metadata": {"movie_id": kwargs["movie_id"]},
    }


def failing_backend(**kwargs):
    raise RuntimeError("backend render failure")


class TestMasterBatch23(unittest.TestCase):
    def test_disabled_adapter_is_safe(self):
        adapter = ProductionBackendAdapter()
        result = adapter.execute("movie-23-001", "A story")
        self.assertFalse(result.accepted)
        self.assertEqual(result.status, "dry_run")

    def test_injected_backend_executes(self):
        adapter = ProductionBackendAdapter(fake_backend, enabled=True)
        result = adapter.execute("movie-23-002", "A story")
        self.assertTrue(result.accepted)
        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.payload["status"], "completed")

    def test_backend_failure_is_normalized(self):
        adapter = ProductionBackendAdapter(failing_backend, enabled=True)
        result = adapter.execute("movie-23-003", "A story")
        self.assertFalse(result.accepted)
        self.assertEqual(result.status, "failed")
        self.assertIn("backend render failure", result.message)

    def test_progress_mapping(self):
        progress = from_pipeline_event(
            "movie-23-004", "final_assembly", 90
        )
        self.assertEqual(progress.status, "running")
        self.assertEqual(progress.progress, 90)

        done = from_pipeline_event(
            "movie-23-004", "publish_readiness", 100
        )
        self.assertEqual(done.status, "completed")

    def test_normalization_and_explicit_switch(self):
        normalized = normalize_backend_result(
            "movie-23-005",
            {"success": True, "status": "completed",
             "output_path": "final.mp4"}
        )
        self.assertTrue(normalized.success)
        self.assertEqual(normalized.artifact_path, "final.mp4")

        switch = ProductionIntegrationSwitch()
        self.assertFalse(switch.enabled)
        switch.enable()
        self.assertTrue(switch.enabled)
        switch.require_enabled()


if __name__ == "__main__":
    unittest.main(verbosity=2)
