from dataclasses import dataclass, field
from typing import Any, Dict


VALID_STATUSES = {
    "queued", "running", "verifying", "repairing",
    "assembling", "completed", "failed", "cancelled"
}


@dataclass
class BackendProductionJob:
    movie_id: str
    pipeline_job_id: str
    status: str = "queued"
    progress: float = 0.0
    current_step: str = "queued"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update(self, status: str, progress: float, current_step: str):
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid status: {status}")
        if not 0.0 <= progress <= 100.0:
            raise ValueError("progress must be between 0 and 100")
        self.status = status
        self.progress = progress
        self.current_step = current_step
