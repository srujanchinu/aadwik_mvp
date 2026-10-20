from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ProgressEvent:
    movie_id: str
    stage: str
    status: str
    progress: float
    message: str = ""
    metadata: Dict = None

class ProgressEventStream:
    def __init__(self):
        self.events: List[ProgressEvent] = []

    def emit(self, movie_id, stage, status, progress, message="",
             metadata=None):
        progress = max(0.0, min(1.0, float(progress)))
        event = ProgressEvent(
            movie_id, stage, status, progress, message, dict(metadata or {})
        )
        self.events.append(event)
        return event

    def latest(self, movie_id):
        items = [e for e in self.events if e.movie_id == movie_id]
        return items[-1] if items else None
