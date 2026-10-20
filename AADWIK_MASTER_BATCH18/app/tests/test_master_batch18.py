import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.integration.render_bridge import RenderBridge
from app.integration.movie_generation_adapter import (
    MovieGenerationAdapter, MovieGenerationRequest
)
from app.integration.progress_events import ProgressEventStream
from app.integration.integration_status import evaluate_status

class FakeRenderer:
    def generate_video(self, prompt, output_path, **kwargs):
        return output_path

class BrokenRenderer:
    def generate_video(self, prompt, output_path, **kwargs):
        raise RuntimeError("renderer unavailable")

class TestBatch18(unittest.TestCase):
    def test_render_bridge_success(self):
        result = RenderBridge(FakeRenderer()).execute(
            "scene prompt", "movie.mp4", aspect_ratio="16:9"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.status, "generated")
        self.assertEqual(result.output_path, "movie.mp4")

    def test_render_bridge_failure(self):
        result = RenderBridge(BrokenRenderer()).execute(
            "scene prompt", "movie.mp4"
        )
        self.assertFalse(result.success)
        self.assertEqual(result.status, "failed")
        self.assertIn("renderer unavailable", result.errors[0])

    def test_movie_generation_adapter(self):
        adapter = MovieGenerationAdapter(RenderBridge(FakeRenderer()))
        request = MovieGenerationRequest(
            "m1", "A cinematic scene", "out.mp4", style="3D"
        )
        result = adapter.generate(request)
        self.assertTrue(result.success)
        self.assertEqual(result.output_path, "out.mp4")

    def test_progress_events(self):
        stream = ProgressEventStream()
        stream.emit("m1", "generation", "running", 0.5, "Rendering")
        stream.emit("m1", "generation", "complete", 1.2, "Done")
        latest = stream.latest("m1")
        self.assertEqual(latest.status, "complete")
        self.assertEqual(latest.progress, 1.0)

    def test_integration_status(self):
        ready = evaluate_status({
            "story": "ready",
            "renderer": "connected",
            "assembly": "ready",
        })
        self.assertTrue(ready.ready)
        blocked = evaluate_status({
            "story": "ready",
            "renderer": "failed",
        })
        self.assertFalse(blocked.ready)
        self.assertEqual(blocked.blockers, ["renderer"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
