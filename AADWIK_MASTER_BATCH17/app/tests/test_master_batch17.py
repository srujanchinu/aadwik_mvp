import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.render.local_execution import LocalCommandExecutor, executable_exists
from app.render.blender_command import BlenderCommand
from app.render.ffmpeg_command import FFmpegCommand
from app.render.local_pipeline import LocalRenderPipeline

class Completed:
    def __init__(self, code=0, stdout="", stderr=""):
        self.returncode = code
        self.stdout = stdout
        self.stderr = stderr

class FakeRunner:
    def __init__(self, codes=None):
        self.codes = list(codes or [0])
        self.calls = []

    def __call__(self, cmd, **kwargs):
        self.calls.append(cmd)
        code = self.codes.pop(0) if self.codes else 0
        return Completed(code, "ok", "" if code == 0 else "failed")

class TestBatch17(unittest.TestCase):
    def test_command_executor(self):
        runner = FakeRunner([0])
        result = LocalCommandExecutor(runner).run(["tool", "--test"], "out.mp4")
        self.assertTrue(result.success)
        self.assertEqual(result.output_path, "out.mp4")
        self.assertEqual(runner.calls[0][0], "tool")

    def test_blender_command(self):
        cmd = BlenderCommand("blender.exe", "scene.blend", "frames/").build()
        self.assertEqual(cmd[0], "blender.exe")
        self.assertIn("BLENDER_EEVEE", cmd)
        self.assertIn("-a", cmd)

    def test_ffmpeg_command(self):
        cmd = FFmpegCommand("ffmpeg.exe", "frame_%04d.png", "shot.mp4").build()
        self.assertEqual(cmd[0], "ffmpeg.exe")
        self.assertIn("libx264", cmd)
        self.assertEqual(cmd[-1], "shot.mp4")

    def test_pipeline_success(self):
        runner = FakeRunner([0, 0])
        result = LocalRenderPipeline(LocalCommandExecutor(runner)).render_and_encode(
            ["blender.exe", "-b", "scene.blend"],
            ["ffmpeg.exe", "-i", "frames"],
            "shot.mp4",
        )
        self.assertTrue(result.success)
        self.assertEqual(result.steps, ["blender", "ffmpeg"])
        self.assertEqual(result.output_path, "shot.mp4")

    def test_pipeline_stops_on_blender_failure(self):
        runner = FakeRunner([1])
        result = LocalRenderPipeline(LocalCommandExecutor(runner)).render_and_encode(
            ["blender.exe", "-b", "scene.blend"],
            ["ffmpeg.exe", "-i", "frames"],
            "shot.mp4",
        )
        self.assertFalse(result.success)
        self.assertEqual(result.steps, ["blender"])
        self.assertEqual(len(runner.calls), 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
