from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ShotContinuity:
    previous_shot: str = ""
    next_shot: str = ""
    required_matches: Dict = field(default_factory=dict)

class ShotContinuityValidator:
    def validate(self, contract, observed: Dict, required: Dict) -> List[str]:
        return [f"continuity_mismatch:{k}" for k, v in required.items()
                if observed.get(k) != v]

    def bridge(self, previous: Dict, current: Dict) -> ShotContinuity:
        matches = {k: current[k] for k in ("characters","location","objects")
                   if k in previous and k in current}
        return ShotContinuity(previous.get("shot_id",""), current.get("shot_id",""), matches)
