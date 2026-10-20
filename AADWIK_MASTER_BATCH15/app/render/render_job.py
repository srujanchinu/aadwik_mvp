from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class RenderJob:
    job_id: str
    shot_id: str
    provider: str = "local_blender"
    output_path: str = ""
    width: int = 640
    height: int = 360
    fps: int = 8
    frames: int = 16
    status: str = "queued"
    metadata: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def start(self):
        self.status = "rendering"

    def complete(self, output_path: Optional[str] = None):
        if output_path:
            self.output_path = output_path
        self.status = "rendered"

    def fail(self, message: str):
        self.errors.append(message)
        self.status = "failed"

    @property
    def duration_seconds(self) -> float:
        return self.frames / self.fps if self.fps else 0.0

class RenderJobFactory:
    def create(self, shot, output_path=""):
        return RenderJob(
            job_id=f"render:{shot.shot_id}",
            shot_id=shot.shot_id,
            output_path=output_path,
            frames=shot.duration_frames,
            metadata={
                "scene_id": shot.scene_id,
                "camera": shot.camera,
            },
        )
