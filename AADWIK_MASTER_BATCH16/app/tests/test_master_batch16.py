import sys
from pathlib import Path
import unittest
import tempfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.render.ffmpeg_assembly import FFmpegAssemblyPlan
from app.render.ffprobe_validation import MediaValidator
from app.render.render_artifact import RenderArtifact
from app.render.final_assembly import FinalAssembly

class TestBatch16(unittest.TestCase):
    def test_ffmpeg_plan(self):
        planner = FFmpegAssemblyPlan()
        command, concat_file = planner.build_concat(
            ["a.mp4", "b.mp4"], "movie.mp4", "C:/ffmpeg/ffmpeg.exe"
        )
        self.assertEqual(concat_file, "movie.mp4.concat.txt")
        self.assertIn("-f", command)
        self.assertIn("concat", command)
        self.assertEqual(command[-1], "movie.mp4")

    def test_concat_materialization(self):
        planner = FFmpegAssemblyPlan()
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "list.txt")
            planner.materialize_concat_file(["a.mp4", "b.mp4"], target)
            text = Path(target).read_text(encoding="utf-8")
            self.assertIn("file 'a.mp4'", text)
            self.assertIn("file 'b.mp4'", text)

    def test_media_validation(self):
        report = MediaValidator().validate(
            {"width":640, "height":360, "fps":8, "duration":2.0},
            {"width":640, "height":360, "fps":8},
        )
        self.assertTrue(report.passed)
        bad = MediaValidator().validate(
            {"width":1280, "height":360, "fps":8, "duration":2.0},
            {"width":640, "height":360, "fps":8},
        )
        self.assertFalse(bad.passed)
        self.assertIn("metadata_mismatch:width", bad.issues)

    def test_artifact_verification(self):
        artifact = RenderArtifact("shot1", "shot1.mp4")
        self.assertFalse(artifact.verified)
        self.assertEqual(artifact.duration, 2.0)
        artifact.mark_verified({"codec":"h264"})
        self.assertTrue(artifact.verified)
        self.assertEqual(artifact.metadata["codec"], "h264")

    def test_final_assembly_gate(self):
        assembly = FinalAssembly("movie1")
        artifact = RenderArtifact("shot1", "shot1.mp4")
        with self.assertRaises(ValueError):
            assembly.add_verified(artifact)
        artifact.mark_verified()
        assembly.add_verified(artifact)
        assembly.mark_ready("movie.mp4")
        self.assertEqual(assembly.status, "ready")
        self.assertEqual(assembly.output_path, "movie.mp4")

if __name__ == "__main__":
    unittest.main(verbosity=2)
