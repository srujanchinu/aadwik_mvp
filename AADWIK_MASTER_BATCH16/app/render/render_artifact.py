from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class RenderArtifact:
    shot_id: str
    path: str
    media_type: str = "video"
    width: int = 640
    height: int = 360
    fps: int = 8
    frames: int = 16
    verified: bool = False
    metadata: Dict = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)

    @property
    def duration(self):
        return self.frames / self.fps if self.fps else 0.0

    def mark_verified(self, metadata=None):
        self.verified = True
        if metadata:
            self.metadata.update(metadata)
