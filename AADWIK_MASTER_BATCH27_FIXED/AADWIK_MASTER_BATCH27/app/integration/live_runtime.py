from dataclasses import dataclass
from typing import Any, Dict

MASTER_RUNTIME_ENABLED = False


@dataclass(frozen=True)
class RuntimeDispatch:
    accepted: bool
    movie_id: str
    status: str
    payload: Dict[str, Any]


def dispatch_master_runtime(movie_id: str, movie: Dict[str, Any]) -> RuntimeDispatch:
    """Guarded handoff. Disabled by default until the live pipeline is enabled."""
    if not MASTER_RUNTIME_ENABLED:
        return RuntimeDispatch(
            accepted=False,
            movie_id=movie_id,
            status="disabled",
            payload={"reason": "master runtime disabled"},
        )

    return RuntimeDispatch(
        accepted=True,
        movie_id=movie_id,
        status="queued",
        payload={
            "movie_id": movie_id,
            "prompt": movie.get("prompt", ""),
            "aspect_ratio": movie.get("aspect_ratio", "16:9"),
            "language": movie.get("language"),
            "style": movie.get("style"),
        },
    )
