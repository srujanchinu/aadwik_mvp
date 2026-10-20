from dataclasses import dataclass


@dataclass
class LiveBackendState:
    movie_id: str
    pipeline_job_id: str
    status: str = "queued"
    progress: float = 0.0

    def update(self, status: str, progress: float):
        if not 0 <= progress <= 100:
            raise ValueError("progress must be between 0 and 100")
        self.status = status
        self.progress = progress
