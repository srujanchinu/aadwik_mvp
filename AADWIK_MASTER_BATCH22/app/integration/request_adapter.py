from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class BackendGenerationRequest:
    movie_id: str
    pipeline_job_id: str
    story: str
    aspect_ratio: str = "16:9"
    style: str | None = None
    metadata: Dict[str, Any] | None = None

    def to_backend_payload(self) -> Dict[str, Any]:
        payload = {
            "movie_id": self.movie_id,
            "pipeline_job_id": self.pipeline_job_id,
            "story": self.story.strip(),
            "aspect_ratio": self.aspect_ratio,
        }
        if self.style:
            payload["style"] = self.style
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload


def normalize_request(movie_id: str, pipeline_job_id: str, story: str, **kwargs):
    if not movie_id or not pipeline_job_id:
        raise ValueError("movie_id and pipeline_job_id are required")
    if not story or not story.strip():
        raise ValueError("story is required")
    return BackendGenerationRequest(
        movie_id=movie_id,
        pipeline_job_id=pipeline_job_id,
        story=story,
        aspect_ratio=kwargs.get("aspect_ratio", "16:9"),
        style=kwargs.get("style"),
        metadata=kwargs.get("metadata"),
    )
