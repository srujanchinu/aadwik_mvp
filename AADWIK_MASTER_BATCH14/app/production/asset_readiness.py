from dataclasses import dataclass, field
from typing import List

@dataclass
class ReadinessReport:
    ready: bool
    missing: List[str] = field(default_factory=list)

class AssetReadinessGate:
    def check(self, requirements, available_ids):
        available = set(available_ids)
        missing = [a.asset_id for a in requirements
                   if a.required and a.asset_id not in available]
        return ReadinessReport(not missing, missing)
