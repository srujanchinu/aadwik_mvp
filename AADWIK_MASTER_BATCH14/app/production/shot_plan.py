from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ShotSpec:
    shot_id: str
    scene_id: str
    purpose: str
    duration_frames: int = 16
    camera: str = "medium"
    characters: List[str] = field(default_factory=list)
    location: str = ""
    objects: List[str] = field(default_factory=list)
    emotion: str = ""
    action: str = ""
    dialogue: str = ""
    visual_prompt: str = ""

    def to_dict(self) -> Dict:
        return {
            "shot_id": self.shot_id, "scene_id": self.scene_id,
            "purpose": self.purpose, "duration_frames": self.duration_frames,
            "camera": self.camera, "characters": list(self.characters),
            "location": self.location, "objects": list(self.objects),
            "emotion": self.emotion, "action": self.action,
            "dialogue": self.dialogue, "visual_prompt": self.visual_prompt,
        }

class ShotPlanner:
    def plan(self, scene: Dict) -> List[ShotSpec]:
        sid = scene["scene_id"]
        chars = list(scene.get("characters", []))
        loc = scene.get("location", "")
        objs = list(scene.get("objects", []))
        emo = scene.get("emotion", "")
        action = scene.get("action", "")
        purpose = scene.get("purpose", "")
        return [
            ShotSpec(f"{sid}_shot_01", sid, purpose, camera="establishing",
                     characters=chars, location=loc, objects=objs,
                     emotion=emo, action=action, visual_prompt=f"Establish {loc}"),
            ShotSpec(f"{sid}_shot_02", sid, purpose, camera="medium_close",
                     characters=chars, location=loc, objects=objs,
                     emotion=emo, action=action, visual_prompt=f"Show character action: {action}"),
        ]
