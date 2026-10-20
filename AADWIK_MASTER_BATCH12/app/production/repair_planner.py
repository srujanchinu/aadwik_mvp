from dataclasses import dataclass, field
from typing import List

@dataclass
class RepairAction:
    target: str
    reason: str
    priority: str = "normal"

@dataclass
class RepairPlan:
    required: bool
    actions: List[RepairAction] = field(default_factory=list)

class RepairPlanner:
    """Turns alignment failures into targeted repair actions."""

    def plan(self, report) -> RepairPlan:
        actions = [
            RepairAction(f.category, f.message, "high" if f.severity == "error" else "normal")
            for f in report.findings
        ]
        return RepairPlan(required=bool(actions), actions=actions)
