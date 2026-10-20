from typing import Callable, Any


class LiveBackendDispatcher:
    """Runtime handoff; disabled unless explicitly enabled."""

    def __init__(self, handler: Callable[..., Any] | None = None, enabled=False):
        self.handler = handler
        self.enabled = bool(enabled)

    def dispatch(self, movie_id: str, pipeline_job_id: str, **payload):
        if not self.enabled:
            return {"accepted": False, "status": "bypassed"}
        if self.handler is None:
            return {"accepted": False, "status": "unconfigured"}
        result = self.handler(
            movie_id=movie_id,
            pipeline_job_id=pipeline_job_id,
            **payload,
        )
        return result if isinstance(result, dict) else {"result": result}
