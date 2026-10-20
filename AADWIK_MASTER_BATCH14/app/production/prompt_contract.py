from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PromptContract:
    shot_id: str
    positive: List[str]
    negative: List[str]
    locked_facts: Dict
    provider: str = "local_blender"

    def render(self) -> str:
        return (
            f"SHOT {self.shot_id}\n"
            f"POSITIVE: {', '.join(self.positive)}\n"
            f"NEGATIVE: {', '.join(self.negative)}\n"
            f"LOCKED: {', '.join(f'{k}={v}' for k,v in self.locked_facts.items())}"
        )

class PromptContractBuilder:
    def build(self, shot, locked_facts=None, negative=None):
        positive = [shot.visual_prompt, f"camera:{shot.camera}",
                    f"emotion:{shot.emotion}", f"action:{shot.action}"]
        return PromptContract(shot.shot_id, [x for x in positive if x and not x.endswith(":")],
                              list(negative or ["identity drift", "wrong location"]),
                              dict(locked_facts or {}))
