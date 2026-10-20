from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime, timezone
import uuid

SCHEMA = "aadwik-production-job-1.0"

VALID_STATES = [
    "CREATED", "PLANNED", "ASSETS_READY", "PRODUCING",
    "AUDIO_READY", "EDITING", "QC", "READY_TO_PUBLISH",
    "PUBLISHED", "FAILED", "RECOVERABLE"
]

@dataclass
class ProductionJob:
    job_id: str
    project_id: str
    production_type: str
    state: str = "CREATED"
    scenes: List[Dict[str, Any]] = field(default_factory=list)
    checkpoints: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

def create_job(project_id, production_type="movie", scenes=None):
    if production_type not in ("movie", "series_episode"):
        raise ValueError("unsupported production type")
    return ProductionJob(
        job_id="job_" + uuid.uuid4().hex[:12],
        project_id=project_id,
        production_type=production_type,
        scenes=scenes or []
    )

def transition(job, new_state):
    if new_state not in VALID_STATES:
        raise ValueError("invalid state")
    job.state = new_state
    return job

def checkpoint(job, name, payload=None):
    job.checkpoints[name] = {
        "completed": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload or {}
    }
    return job

def fail(job, error, recoverable=True):
    job.errors.append(str(error))
    job.state = "RECOVERABLE" if recoverable else "FAILED"
    return job

def build_production_package(job):
    return {
        "schema": SCHEMA,
        "job_id": job.job_id,
        "project_id": job.project_id,
        "production_type": job.production_type,
        "state": job.state,
        "scene_count": len(job.scenes),
        "checkpoints": job.checkpoints,
        "errors": job.errors,
    }
