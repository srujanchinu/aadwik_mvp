from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class OrchestrationResult:
    project_id: str
    status: str
    completed_steps: List[str] = field(default_factory=list)
    blocked_steps: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

class MasterOrchestrator:
    """Thin integration layer for the independent Aadwik engines.

    This deliberately does not replace the existing backend movie pipeline.
    It provides a deterministic, testable coordination contract that can later
    be wired into the production API.
    """
    ORDER = [
        "story_understanding",
        "scene_breakdown",
        "character_world_lock",
        "shot_planning",
        "generation",
        "alignment_verification",
        "repair",
        "final_assembly",
    ]

    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def run(self, project_id: str, steps: Optional[List[str]] = None,
            context: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        requested = steps or self.ORDER
        unknown = [s for s in requested if s not in self.ORDER]
        if unknown:
            return OrchestrationResult(
                project_id=project_id, status="blocked",
                blocked_steps=unknown,
                errors=[f"Unknown pipeline step: {s}" for s in unknown],
                context=dict(context or {}),
            )

        completed = []
        blocked = []
        ctx = dict(context or {})
        for step in self.ORDER:
            if step not in requested:
                continue
            if step == "repair" and not ctx.get("repair_required", False):
                completed.append("repair_not_required")
                continue
            if ctx.get("blocked_at") == step:
                blocked.append(step)
                break
            completed.append(step)
            ctx[f"{step}_complete"] = True

        status = "blocked" if blocked else "complete"
        result = OrchestrationResult(project_id, status, completed, blocked, [], ctx)
        self.history.append({
            "project_id": project_id,
            "status": status,
            "completed_steps": list(completed),
            "blocked_steps": list(blocked),
        })
        return result
