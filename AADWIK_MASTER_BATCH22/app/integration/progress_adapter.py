from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineProgressEvent:
    job_id: str
    step: str
    progress: float


STEP_MAP = {
    "story_understanding": ("running", 5.0),
    "scene_breakdown": ("running", 15.0),
    "character_world_lock": ("running", 25.0),
    "shot_planning": ("running", 35.0),
    "generation": ("running", 55.0),
    "alignment_verification": ("verifying", 70.0),
    "repair": ("repairing", 80.0),
    "final_assembly": ("assembling", 90.0),
    "quality_gate": ("assembling", 95.0),
    "publish_readiness": ("completed", 100.0),
}


def adapt_progress(event: PipelineProgressEvent) -> dict:
    if event.step not in STEP_MAP:
        raise ValueError(f"unknown pipeline step: {event.step}")
    status, default_progress = STEP_MAP[event.step]
    progress = event.progress if event.progress >= 0 else default_progress
    if not 0 <= progress <= 100:
        raise ValueError("progress must be between 0 and 100")
    return {
        "pipeline_job_id": event.job_id,
        "status": status,
        "progress": progress,
        "current_step": event.step,
    }
