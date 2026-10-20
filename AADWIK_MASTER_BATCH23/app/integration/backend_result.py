from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class NormalizedBackendResult:
    success: bool
    movie_id: str
    status: str
    artifact_path: str | None = None
    error: str | None = None
    metadata: Dict[str, Any] | None = None


def normalize_backend_result(movie_id: str, result: Any) -> NormalizedBackendResult:
    if isinstance(result, dict):
        success = bool(result.get("success", result.get("status") in {"accepted", "completed"}))
        return NormalizedBackendResult(
            success=success,
            movie_id=movie_id,
            status=str(result.get("status", "unknown")),
            artifact_path=result.get("artifact_path") or result.get("output_path"),
            error=result.get("error"),
            metadata=result.get("metadata"),
        )

    return NormalizedBackendResult(
        success=bool(result),
        movie_id=movie_id,
        status="completed" if result else "failed",
    )
