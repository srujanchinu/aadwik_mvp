from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class MovieJobMapping:
    movie_id: str
    pipeline_job_id: str
    story: str
    aspect_ratio: str = "16:9"
    style: str | None = None

    def to_backend_payload(self) -> Dict[str, Any]:
        payload = {
            "movie_id": self.movie_id,
            "pipeline_job_id": self.pipeline_job_id,
            "story": self.story,
            "aspect_ratio": self.aspect_ratio,
        }
        if self.style:
            payload["style"] = self.style
        return payload


def map_movie_job(movie_id: str, pipeline_job_id: str, story: str, **kwargs) -> MovieJobMapping:
    if not movie_id or not pipeline_job_id:
        raise ValueError("movie_id and pipeline_job_id are required")
    if not story.strip():
        raise ValueError("story is required")
    return MovieJobMapping(movie_id, pipeline_job_id, story.strip(), **kwargs)
