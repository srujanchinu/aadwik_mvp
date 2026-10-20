from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ExecutionContract:
    shot_id: str
    required_assets: List[str] = field(default_factory=list)
    provider: str = ""
    output_path: str = ""
    expected_metadata: Dict = field(default_factory=dict)
    status: str = "planned"

    def mark_generating(self):
        self.status = "generating"

    def mark_complete(self, output_path: str = ""):
        if output_path:
            self.output_path = output_path
        self.status = "generated"

    def mark_failed(self):
        self.status = "failed"

class ExecutionContractBuilder:
    def build(self, shot, assets, provider="local_blender") -> ExecutionContract:
        return ExecutionContract(
            shot_id=shot.shot_id,
            required_assets=[a.asset_id for a in assets],
            provider=provider,
            expected_metadata={
                "scene_id": shot.scene_id,
                "duration_frames": shot.duration_frames,
                "camera": shot.camera,
            },
        )
