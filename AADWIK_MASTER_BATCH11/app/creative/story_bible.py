from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class StoryBible:
    title: str
    genre: str
    tone: str = ""
    premise: str = ""
    characters: Dict[str, Dict] = field(default_factory=dict)
    locations: Dict[str, Dict] = field(default_factory=dict)
    rules: List[str] = field(default_factory=list)
    objects: Dict[str, Dict] = field(default_factory=dict)
    canon_version: int = 1

    def add_character(self, name: str, profile: Dict) -> None:
        self.characters[name] = dict(profile)

    def add_location(self, name: str, profile: Dict) -> None:
        self.locations[name] = dict(profile)

    def add_object(self, name: str, profile: Dict) -> None:
        self.objects[name] = dict(profile)

    def add_rule(self, rule: str) -> None:
        if rule not in self.rules:
            self.rules.append(rule)

    def snapshot(self) -> Dict:
        return {
            "title": self.title,
            "genre": self.genre,
            "tone": self.tone,
            "premise": self.premise,
            "characters": dict(self.characters),
            "locations": dict(self.locations),
            "rules": list(self.rules),
            "objects": dict(self.objects),
            "canon_version": self.canon_version,
        }

    def bump_canon(self) -> int:
        self.canon_version += 1
        return self.canon_version

class CanonGuard:
    def __init__(self, bible: StoryBible):
        self.bible = bible

    def validate(self, scene: Dict) -> List[str]:
        issues = []
        for name in scene.get("characters", []):
            if name not in self.bible.characters:
                issues.append(f"unknown_character:{name}")
        for name in scene.get("locations", []):
            if name not in self.bible.locations:
                issues.append(f"unknown_location:{name}")
        for name in scene.get("objects", []):
            if name not in self.bible.objects:
                issues.append(f"unknown_object:{name}")
        return issues
