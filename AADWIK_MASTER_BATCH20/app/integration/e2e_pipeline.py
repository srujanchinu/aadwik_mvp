from dataclasses import dataclass, field
from typing import Dict, List


STAGES = [
    "story_understanding",
    "scene_breakdown",
    "character_world_lock",
    "shot_planning",
    "generation",
    "alignment_verification",
    "repair",
    "final_assembly",
    "quality_gate",
    "publish_readiness",
]


@dataclass
class StageRecord:
    name: str
    status: str = "pending"
    message: str = ""


@dataclass
class EndToEndResult:
    job_id: str
    status: str
    stages: List[StageRecord] = field(default_factory=list)
    artifact: Dict = field(default_factory=dict)

    @property
    def completed_stages(self) -> List[str]:
        return [s.name for s in self.stages if s.status == "passed"]


class EndToEndPipeline:
    """Deterministic integration contract for the complete Aadwik production flow."""

    def __init__(self):
        self.stage_order = list(STAGES)

    def run(self, job_id: str, story: str, fail_at: str | None = None) -> EndToEndResult:
        if not job_id:
            raise ValueError("job_id is required")
        if not story or not story.strip():
            raise ValueError("story is required")

        records = []
        for stage in self.stage_order:
            record = StageRecord(stage)
            if fail_at == stage:
                record.status = "failed"
                record.message = f"Stage failed: {stage}"
                records.append(record)
                return EndToEndResult(job_id, "failed", records)

            record.status = "passed"
            record.message = f"Stage passed: {stage}"
            records.append(record)

        artifact = {
            "job_id": job_id,
            "story": story,
            "production_status": "complete",
            "publish_ready": True,
            "stage_count": len(records),
        }
        return EndToEndResult(job_id, "complete", records, artifact)
