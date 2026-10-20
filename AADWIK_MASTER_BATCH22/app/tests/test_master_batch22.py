import unittest

from app.integration.backend_job import BackendProductionJob
from app.integration.request_adapter import normalize_request
from app.integration.progress_adapter import PipelineProgressEvent, adapt_progress
from app.integration.status_sync import StatusSynchronizer
from app.integration.failure_adapter import normalize_failure


class TestMasterBatch22(unittest.TestCase):
    def test_backend_job_lifecycle_update(self):
        job = BackendProductionJob("movie-22-001", "pipeline-22-001")
        job.update("running", 55.0, "generation")
        self.assertEqual(job.status, "running")
        self.assertEqual(job.progress, 55.0)
        self.assertEqual(job.current_step, "generation")

    def test_request_normalization(self):
        request = normalize_request(
            "movie-22-002", "pipeline-22-002",
            "  A glowing star story.  ",
            aspect_ratio="16:9", style="cinematic"
        )
        payload = request.to_backend_payload()
        self.assertEqual(payload["story"], "A glowing star story.")
        self.assertEqual(payload["style"], "cinematic")

    def test_progress_adapter(self):
        event = PipelineProgressEvent(
            "pipeline-22-003", "alignment_verification", 72.0
        )
        result = adapt_progress(event)
        self.assertEqual(result["status"], "verifying")
        self.assertEqual(result["progress"], 72.0)

    def test_status_sync_blocks_terminal_regression(self):
        sync = StatusSynchronizer()
        sync.apply("movie-22-004", {"status": "completed", "progress": 100})
        with self.assertRaises(ValueError):
            sync.apply("movie-22-004", {"status": "running", "progress": 50})

    def test_failure_normalization(self):
        failure = normalize_failure(
            RuntimeError("render failed"), "generation", retryable=True
        )
        self.assertEqual(failure.code, "RuntimeError")
        self.assertEqual(failure.stage, "generation")
        self.assertTrue(failure.retryable)


if __name__ == "__main__":
    unittest.main(verbosity=2)
