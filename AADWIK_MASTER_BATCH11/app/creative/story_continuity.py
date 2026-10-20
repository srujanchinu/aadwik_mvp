from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ContinuityState:
    scene_index: int = 0
    character_states: Dict[str, Dict] = field(default_factory=dict)
    location_states: Dict[str, Dict] = field(default_factory=dict)
    object_states: Dict[str, Dict] = field(default_factory=dict)

class StoryContinuityTracker:
    """Tracks explicit state between scenes; it never invents missing canon."""

    def __init__(self):
        self.state = ContinuityState()

    def apply_scene(self, scene_index: int, updates: Dict) -> ContinuityState:
        self.state.scene_index = scene_index
        for key, value in updates.get("characters", {}).items():
            self.state.character_states[key] = dict(value)
        for key, value in updates.get("locations", {}).items():
            self.state.location_states[key] = dict(value)
        for key, value in updates.get("objects", {}).items():
            self.state.object_states[key] = dict(value)
        return self.state

    def get_character(self, name: str):
        return self.state.character_states.get(name)

    def get_object(self, name: str):
        return self.state.object_states.get(name)
