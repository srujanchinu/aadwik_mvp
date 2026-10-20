from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class BackendJob:
    movie_id: str
    story: str
    status: str = "created"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BridgeResult:
    accepted: bool
    movie_id: str
    message: str
    payload: Dict[str, Any] = field(default_factory=dict)


class BackendBridge:
    """Safe adapter contract for wiring the master pipeline to the movie backend."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def prepare_job(self, movie_id: str, story: str, **metadata) -> BackendJob:
        if not movie_id:
            raise ValueError("movie_id is required")
        if not story or not story.strip():
            raise ValueError("story is required")
        return BackendJob(movie_id=movie_id, story=story.strip(), metadata=dict(metadata))

    def submit(self, job: BackendJob) -> BridgeResult:
        if not self.enabled:
            return BridgeResult(
                False, job.movie_id, "backend bridge disabled",
                {"dry_run": True, "movie_id": job.movie_id}
            )
        job.status = "accepted"
        return BridgeResult(
            True, job.movie_id, "job accepted by integration bridge",
            {"movie_id": job.movie_id, "story": job.story, **job.metadata}
        )
