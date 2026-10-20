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
            "shot_id": self.shot_id,
            "scene_id": self.scene_id,
            "purpose": self.purpose,
            "duration_frames": self.duration_frames,
            "camera": self.camera,
            "characters": list(self.characters),
            "location": self.location,
            "objects": list(self.objects),
            "emotion": self.emotion,
            "action": self.action,
            "dialogue": self.dialogue,
            "visual_prompt": self.visual_prompt,
        }

class ShotPlanner:
    """Creates explicit shot contracts from scene-level intent."""

    def plan(self, scene: Dict) -> List[ShotSpec]:
        scene_id = scene["scene_id"]
        characters = list(scene.get("characters", []))
        location = scene.get("location", "")
        objects = list(scene.get("objects", []))
        emotion = scene.get("emotion", "")
        action = scene.get("action", "")
        purpose = scene.get("purpose", "")

        return [
            ShotSpec(
                f"{scene_id}_shot_01", scene_id, purpose,
                camera="establishing", characters=characters,
                location=location, objects=objects, emotion=emotion,
                action=action, visual_prompt=f"Establish {location}"
            ),
            ShotSpec(
                f"{scene_id}_shot_02", scene_id, purpose,
                camera="medium_close", characters=characters,
                location=location, objects=objects, emotion=emotion,
                action=action, visual_prompt=f"Show character action: {action}"
            ),
        ]
