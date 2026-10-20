from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class SceneIntent:
    scene_id: str
    purpose: str
    emotional_goal: str = ""
    required_characters: List[str] = field(default_factory=list)
    required_locations: List[str] = field(default_factory=list)
    required_objects: List[str] = field(default_factory=list)
    visual_beats: List[str] = field(default_factory=list)
    dialogue_beats: List[str] = field(default_factory=list)
    learning_beats: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "scene_id": self.scene_id,
            "purpose": self.purpose,
            "emotional_goal": self.emotional_goal,
            "required_characters": list(self.required_characters),
            "required_locations": list(self.required_locations),
            "required_objects": list(self.required_objects),
            "visual_beats": list(self.visual_beats),
            "dialogue_beats": list(self.dialogue_beats),
            "learning_beats": list(self.learning_beats),
        }

def validate_scene_intent(intent: SceneIntent) -> List[str]:
    issues = []
    if not intent.scene_id:
        issues.append("missing_scene_id")
    if not intent.purpose:
        issues.append("missing_purpose")
    return issues
