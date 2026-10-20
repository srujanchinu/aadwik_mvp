import unittest

from app.integration.live_movie_hook import LiveMovieHook
from app.integration.movies_wiring import validate_target_text
from app.integration.wiring_marker import MARKER, has_marker, marker_block


def fake_runner(**kwargs):
    return {"status": "accepted", "movie_id": kwargs["movie_id"]}


class TestMasterBatch24(unittest.TestCase):
    def test_live_hook_is_safe_by_default(self):
        hook = LiveMovieHook()
        result = hook.invoke("movie-24-001", "A story")
        self.assertFalse(result.handled)
        self.assertEqual(result.status, "bypassed")

    def test_live_hook_can_be_enabled_with_injected_runner(self):
        hook = LiveMovieHook(enabled=True, runner=fake_runner)
        result = hook.invoke("movie-24-002", "A story")
        self.assertTrue(result.handled)
        self.assertEqual(result.payload["status"], "accepted")

    def test_target_validation_requires_movies_router_shape(self):
        valid = "from fastapi import APIRouter\nrouter = APIRouter()\n# /movies"
        self.assertTrue(validate_target_text(valid))
        self.assertFalse(validate_target_text("print('hello')"))

    def test_marker_is_deterministic(self):
        block = marker_block()
        self.assertIn(MARKER, block)
        self.assertTrue(has_marker(block))
        self.assertFalse(has_marker("router = APIRouter()"))

    def test_runner_failure_is_normalized(self):
        def broken(**kwargs):
            raise RuntimeError("generation failed")

        hook = LiveMovieHook(enabled=True, runner=broken)
        result = hook.invoke("movie-24-003", "A story")
        self.assertFalse(result.handled)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.payload["error_type"], "RuntimeError")


if __name__ == "__main__":
    unittest.main(verbosity=2)
