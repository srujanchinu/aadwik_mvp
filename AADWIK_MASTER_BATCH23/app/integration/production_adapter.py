from dataclasses import dataclass, field
from typing import Any, Callable, Dict


@dataclass(frozen=True)
class AdapterResult:
    accepted: bool
    movie_id: str
    status: str
    message: str
    payload: Dict[str, Any] = field(default_factory=dict)


class ProductionBackendAdapter:
    """Injectable boundary between Aadwik master pipeline and movie backend."""

    def __init__(self, backend_callable: Callable[..., Any] | None = None,
                 enabled: bool = False):
        self.backend_callable = backend_callable
        self.enabled = enabled

    def execute(self, movie_id: str, story: str, **kwargs) -> AdapterResult:
        if not movie_id:
            raise ValueError("movie_id is required")
        if not story or not story.strip():
            raise ValueError("story is required")

        if not self.enabled:
            return AdapterResult(
                False, movie_id, "dry_run",
                "production adapter disabled",
                {"movie_id": movie_id, "story": story.strip()}
            )

        if self.backend_callable is None:
            return AdapterResult(
                False, movie_id, "failed",
                "backend callable is not configured",
                {}
            )

        try:
            result = self.backend_callable(
                movie_id=movie_id,
                story=story.strip(),
                **kwargs,
            )
            payload = result if isinstance(result, dict) else {"result": result}
            return AdapterResult(
                True, movie_id, "accepted",
                "backend execution accepted",
                payload,
            )
        except Exception as exc:
            return AdapterResult(
                False, movie_id, "failed",
                str(exc) or "backend execution failed",
                {"error_type": exc.__class__.__name__},
            )
