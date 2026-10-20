from dataclasses import dataclass, field
from typing import Any, Callable, Dict


@dataclass
class RuntimeJob:
    movie_id: str
    story: str
    status: str = "queued"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeResult:
    accepted: bool
    movie_id: str
    status: str
    payload: Dict[str, Any]


class MasterRuntimeBridge:
    """Explicit bridge from a backend movie job into the master pipeline."""

    def __init__(self, enabled=False, pipeline_runner=None):
        self.enabled = bool(enabled)
        self.pipeline_runner = pipeline_runner

    def create_job(self, movie_id, story, **metadata):
        if not movie_id:
            raise ValueError("movie_id is required")
        if not story or not story.strip():
            raise ValueError("story is required")
        return RuntimeJob(movie_id, story.strip(), metadata=metadata)

    def dispatch(self, job: RuntimeJob) -> RuntimeResult:
        if not self.enabled:
            return RuntimeResult(False, job.movie_id, "bypassed",
                                 {"reason": "master runtime bridge disabled"})
        if self.pipeline_runner is None:
            return RuntimeResult(False, job.movie_id, "unconfigured",
                                 {"reason": "pipeline runner not configured"})
        try:
            result = self.pipeline_runner(
                movie_id=job.movie_id, story=job.story, **job.metadata
            )
            payload = result if isinstance(result, dict) else {"result": result}
            job.status = "running"
            return RuntimeResult(True, job.movie_id, "dispatched", payload)
        except Exception as exc:
            job.status = "failed"
            return RuntimeResult(False, job.movie_id, "failed",
                                 {"error": str(exc),
                                  "error_type": exc.__class__.__name__})
