import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.render.render_job import RenderJob, RenderJobFactory
from app.render.provider_adapter import ProviderAdapter
from app.render.render_validator import RenderValidator
from app.render.render_queue import RenderQueue

class FakeProvider:
    def generate_video(self, prompt, output_path, **kwargs):
        return output_path

class FailingProvider:
    def generate_video(self, prompt, output_path, **kwargs):
        raise RuntimeError("render failed")

class Shot:
    shot_id = "s1_shot_01"
    scene_id = "s1"
    duration_frames = 16
    camera = "medium_close"

class TestBatch15(unittest.TestCase):
    def test_render_job(self):
        job = RenderJobFactory().create(Shot(), "shot.mp4")
        self.assertEqual(job.status, "queued")
        self.assertEqual(job.duration_seconds, 2.0)
        job.start()
        job.complete()
        self.assertEqual(job.status, "rendered")
        self.assertEqual(job.output_path, "shot.mp4")

    def test_provider_adapter_success(self):
        result = ProviderAdapter(FakeProvider()).generate(
            "test prompt", "shot.mp4", aspect_ratio="16:9"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.output_path, "shot.mp4")

    def test_provider_adapter_failure(self):
        result = ProviderAdapter(FailingProvider()).generate(
            "test prompt", "shot.mp4"
        )
        self.assertFalse(result.success)
        self.assertIn("render failed", result.error)

    def test_render_validation(self):
        job = RenderJob("j", "s", output_path="x.mp4")
        self.assertTrue(RenderValidator().validate_job(job).passed)
        job.fps = 0
        report = RenderValidator().validate_job(job)
        self.assertFalse(report.passed)
        self.assertIn("invalid_fps", report.issues)

    def test_render_queue(self):
        queue = RenderQueue()
        a = RenderJob("a", "s1")
        b = RenderJob("b", "s2")
        queue.enqueue(a)
        queue.enqueue(b)
        self.assertEqual(queue.next().job_id, "a")
        a.complete("a.mp4")
        b.fail("boom")
        self.assertEqual(len(queue.completed()), 1)
        self.assertEqual(len(queue.failed()), 1)
        self.assertEqual(len(queue.pending()), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
