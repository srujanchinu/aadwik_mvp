from dataclasses import dataclass, field
from typing import List

@dataclass
class AssemblyResult:
    success: bool
    output_path: str = ""
    command: List[str] = field(default_factory=list)
    error: str = ""

class FFmpegAssemblyPlan:
    """Builds an explicit FFmpeg concat assembly command.

    Execution is intentionally separate so the production backend can decide
    when/how to invoke the installed FFmpeg binary.
    """

    def build_concat(self, shot_paths, output_path, ffmpeg_path="ffmpeg"):
        paths = list(shot_paths)
        if not paths:
            raise ValueError("no_shots_to_assemble")

        # concat demuxer expects a text file. The caller can materialize
        # concat_file_path and then execute this command.
        concat_file_path = output_path + ".concat.txt"
        command = [
            ffmpeg_path, "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file_path, "-c", "copy", output_path
        ]
        return command, concat_file_path

    def materialize_concat_file(self, shot_paths, concat_file_path):
        with open(concat_file_path, "w", encoding="utf-8") as f:
            for path in shot_paths:
                safe = str(path).replace("'", "'\\''")
                f.write(f"file '{safe}'\n")
        return concat_file_path
