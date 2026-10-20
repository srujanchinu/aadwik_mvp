from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class GenerationAttempt:
    shot_id: str
    provider: str
    status: str
    output: str = ""
    metadata: Dict = field(default_factory=dict)

class GenerationManifest:
    """Auditable record of generation attempts and verification state."""

    def __init__(self):
        self.attempts: List[GenerationAttempt] = []

    def record(self, shot_id: str, provider: str, status: str,
               output: str = "", metadata=None) -> GenerationAttempt:
        attempt = GenerationAttempt(
            shot_id, provider, status, output, dict(metadata or {})
        )
        self.attempts.append(attempt)
        return attempt

    def for_shot(self, shot_id: str) -> List[GenerationAttempt]:
        return [a for a in self.attempts if a.shot_id == shot_id]

    def latest(self, shot_id: str):
        items = self.for_shot(shot_id)
        return items[-1] if items else None
