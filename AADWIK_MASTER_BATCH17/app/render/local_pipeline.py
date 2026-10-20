from dataclasses import dataclass, field
from typing import List

@dataclass
class LocalPipelineResult:
    success: bool
    steps: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    output_path: str = ""

class LocalRenderPipeline:
    """Coordinates Blender and FFmpeg commands without hardcoding execution."""

    def __init__(self, executor):
        self.executor = executor

    def render_and_encode(self, blender_command, ffmpeg_command, output_path):
        steps, errors = [], []

        blender = self.executor.run(blender_command)
        steps.append("blender")
        if not blender.success:
            errors.append(blender.stderr or "blender_failed")
            return LocalPipelineResult(False, steps, errors, "")

        ffmpeg = self.executor.run(ffmpeg_command, output_path=output_path)
        steps.append("ffmpeg")
        if not ffmpeg.success:
            errors.append(ffmpeg.stderr or "ffmpeg_failed")
            return LocalPipelineResult(False, steps, errors, "")

        return LocalPipelineResult(True, steps, errors, output_path)
