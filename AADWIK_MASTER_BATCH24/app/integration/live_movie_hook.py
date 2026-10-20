from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass(frozen=True)
class LiveHookResult:
    handled: bool
    movie_id: str
    status: str
    payload: Dict[str, Any]


class LiveMovieHook:
    """Small, injectable hook for the existing movie-generation endpoint."""

    def __init__(self, enabled: bool = False,
                 runner: Callable[..., Any] | None = None):
        self.enabled = bool(enabled)
        self.runner = runner

    def invoke(self, movie_id: str, story: str, **kwargs) -> LiveHookResult:
        if not movie_id:
            raise ValueError("movie_id is required")
        if not story or not story.strip():
            raise ValueError("story is required")

        if not self.enabled:
            return LiveHookResult(
                False, movie_id, "bypassed",
                {"reason": "live hook disabled"}
            )

        if self.runner is None:
            return LiveHookResult(
                False, movie_id, "unconfigured",
                {"reason": "live runner not configured"}
            )

        try:
            result = self.runner(
                movie_id=movie_id,
                story=story.strip(),
                **kwargs,
            )
            payload = result if isinstance(result, dict) else {"result": result}
            return LiveHookResult(True, movie_id, "handled", payload)
        except Exception as exc:
            return LiveHookResult(
                False, movie_id, "failed",
                {"error": str(exc), "error_type": exc.__class__.__name__}
            )
