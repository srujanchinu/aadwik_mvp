from dataclasses import dataclass
from typing import List

@dataclass
class FFmpegCommand:
    executable: str
    input_pattern: str
    output_path: str
    fps: int = 8
    width: int = 640
    height: int = 360

    def build(self) -> List[str]:
        return [
            self.executable, "-y",
            "-framerate", str(self.fps),
            "-i", self.input_pattern,
            "-vf", f"scale={self.width}:{self.height}",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            self.output_path,
        ]
