import tempfile
import unittest
from pathlib import Path

from app.integration.live_runtime import dispatch_master_runtime
from app.integration.live_patch import (
    compatible_movies_file, already_patched, patch_text, MARKER
)


class TestMasterBatch27(unittest.TestCase):
    def test_runtime_is_disabled_by_default(self):
        result = dispatch_master_runtime("movie-27-001", {"prompt": "story"})
        self.assertFalse(result.accepted)
        self.assertEqual(result.status, "disabled")

    def test_movies_shape_is_validated(self):
        source = (
            "def create_movie(payload, background_tasks):\n"
            "    created_movie = store.create(movie)\n"
            "    background_tasks.add_task(run_movie_generation, movie_id)\n"
        )
        self.assertTrue(compatible_movies_file(source))
        self.assertFalse(compatible_movies_file("print('x')"))

    def test_patch_adds_guarded_hook(self):
        source = (
            "from app.providers.local_video_provider import LocalVideoProvider\n"
            "def create_movie(payload, background_tasks):\n"
            "    created_movie = store.create(\n"
            "        movie\n"
            "    )\n"
            "    background_tasks.add_task(\n"
            "        run_movie_generation,\n"
            "        movie_id,\n"
            "    )\n"
        )
        patched = patch_text(source)
        self.assertIn(MARKER, patched)
        self.assertIn("dispatch_master_runtime(movie_id, created_movie)", patched)
        self.assertTrue(already_patched(patched))

    def test_patch_is_idempotent(self):
        source = (
            "from app.providers.local_video_provider import LocalVideoProvider\n"
            "def create_movie(payload, background_tasks):\n"
            "    created_movie = store.create(\n"
            "        movie\n"
            "    )\n"
            "    background_tasks.add_task(run_movie_generation, movie_id)\n"
        )
        once = patch_text(source)
        twice = patch_text(once)
        self.assertEqual(once, twice)

    def test_patched_file_can_be_written(self):
        source = (
            "from app.providers.local_video_provider import LocalVideoProvider\n"
            "def create_movie(payload, background_tasks):\n"
            "    created_movie = store.create(\n"
            "        movie\n"
            "    )\n"
            "    background_tasks.add_task(run_movie_generation, movie_id)\n"
        )
        patched = patch_text(source)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "movies.py"
            path.write_text(patched, encoding="utf-8")
            self.assertIn(MARKER, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
