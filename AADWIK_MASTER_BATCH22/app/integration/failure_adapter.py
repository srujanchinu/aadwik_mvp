from dataclasses import dataclass


@dataclass(frozen=True)
class BackendFailure:
    code: str
    message: str
    retryable: bool = False
    stage: str | None = None


def normalize_failure(error: Exception, stage: str, retryable: bool = False) -> BackendFailure:
    return BackendFailure(
        code=error.__class__.__name__,
        message=str(error) or "pipeline failure",
        retryable=retryable,
        stage=stage,
    )
