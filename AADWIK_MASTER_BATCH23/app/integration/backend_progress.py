from dataclasses import dataclass


@dataclass(frozen=True)
class BackendProgress:
    movie_id: str
    status: str
    progress: float
    step: str


def from_pipeline_event(movie_id: str, step: str, progress: float) -> BackendProgress:
    if not movie_id:
        raise ValueError("movie_id is required")
    if not step:
        raise ValueError("step is required")
    if not 0 <= progress <= 100:
        raise ValueError("progress must be between 0 and 100")

    status = "completed" if progress >= 100 else "running"
    return BackendProgress(movie_id, status, progress, step)
