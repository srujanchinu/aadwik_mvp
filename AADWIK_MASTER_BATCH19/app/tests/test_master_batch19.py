import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.integration.movie_pipeline_adapter import MoviePipelineAdapter, SafeGenerationController
from app.integration.movie_state_adapter import MovieStateAdapter
from app.integration.generation_guard import GenerationGuard
from app.integration.progress_events import ProgressEventStream

class FakeRenderer:
    def generate_video(self, prompt, output_path, **kwargs):
        return output_path

class BrokenRenderer:
    def generate_video(self, prompt, output_path, **kwargs):
        raise RuntimeError("renderer failed")

class TestBatch19(unittest.TestCase):
    def test_pipeline_success(self):
        stream = ProgressEventStream()
        result = MoviePipelineAdapter(FakeRenderer(), stream).generate(
            "m1", "scene", "movie.mp4", style="3D")
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.output_path, "movie.mp4")
        self.assertEqual(stream.latest("m1").progress, 1.0)

    def test_pipeline_failure(self):
        result = MoviePipelineAdapter(BrokenRenderer()).generate(
            "m2", "scene", "movie.mp4")
        self.assertEqual(result.status, "failed")
        self.assertIn("renderer failed", result.errors[0])

    def test_movie_state(self):
        result = MoviePipelineAdapter(FakeRenderer()).generate(
            "m3", "scene", "movie.mp4")
        state = MovieStateAdapter().apply(result)
        self.assertEqual(state.status, "completed")
        self.assertEqual(state.output_path, "movie.mp4")
        self.assertEqual(state.current_step, "generation")

    def test_generation_guard(self):
        guard = GenerationGuard()
        self.assertTrue(guard.check("m1", "prompt", "out.mp4").allowed)
        blocked = guard.check("", "", "", enabled=False)
        self.assertFalse(blocked.allowed)
        self.assertIn("generation_disabled", blocked.reasons)
        self.assertIn("missing_prompt", blocked.reasons)

    def test_controller(self):
        controller = SafeGenerationController(True)
        self.assertTrue(controller.can_generate())
        controller.disable()
        self.assertFalse(controller.can_generate())
        controller.enable()
        self.assertTrue(controller.can_generate())

if __name__ == "__main__":
    unittest.main(verbosity=2)
