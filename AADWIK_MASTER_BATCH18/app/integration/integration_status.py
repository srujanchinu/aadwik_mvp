from dataclasses import dataclass
from typing import Dict, List

@dataclass
class IntegrationStatus:
    ready: bool
    components: Dict[str, str]
    blockers: List[str]

def evaluate_status(components: Dict[str, str]) -> IntegrationStatus:
    blockers = [
        name for name, status in components.items()
        if status not in ("ready", "connected")
    ]
    return IntegrationStatus(not blockers, dict(components), blockers)
