"""
Aadwik Phase 23 Character Quality — live backend dependency.
Dependency-free runtime module for Blender 5.2 EEVEE.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class CharacterQuality:
    character_id: str
    name: str
    identity_locked: bool = True


CHARACTERS = {
    "tara": CharacterQuality("char_tara_v2", "Tara"),
    "guardian": CharacterQuality("char_guardian_v2", "Guardian"),
    "shadow": CharacterQuality("char_shadow_creature_v2", "Shadow"),
    "blue_star": CharacterQuality("prop_blue_star_v2", "Blue Star"),
}


def build_character(character_id: str, **kwargs) -> Dict[str, Any]:
    if character_id not in CHARACTERS:
        raise ValueError(f"Unknown character: {character_id}")
    q = CHARACTERS[character_id]
    result = {
        "character_id": q.character_id,
        "name": q.name,
        "identity_locked": q.identity_locked,
    }
    result.update(kwargs)
    return result


def apply_emotion(character: Any, emotion: str):
    """Best-effort emotion marker used by the cinematic scene."""
    if character is None:
        return character
    try:
        character["emotion"] = emotion
    except Exception:
        pass
    return character


def direct_character_gaze(character: Any, target: Any):
    """Best-effort gaze target marker; actual Blender constraints remain scene-owned."""
    if character is None:
        return character
    try:
        character["gaze_target"] = target
    except Exception:
        pass
    return character


def get_character_quality(character_id: str) -> Dict[str, Any]:
    return build_character(character_id)
