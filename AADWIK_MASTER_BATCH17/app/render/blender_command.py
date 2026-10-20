from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BlenderCommand:
    executable: str
    scene_file: str
    output_dir: str
    frames: Optional[int] = None

    def build(self) -> List[str]:
        cmd = [
            self.executable, "-b", self.scene_file,
            "-E", "BLENDER_EEVEE",
            "-o", self.output_dir,
            "-a",
        ]
        return cmd
