from dataclasses import dataclass
from typing import Dict, Any


TERMINAL = {"completed", "failed", "cancelled"}


@dataclass
class StatusSynchronizer:
    jobs: Dict[str, Dict[str, Any]]

    def __init__(self):
        self.jobs = {}

    def apply(self, movie_id: str, status_payload: Dict[str, Any]) -> Dict[str, Any]:
        if not movie_id:
            raise ValueError("movie_id is required")
        previous = self.jobs.get(movie_id, {})
        current = dict(previous)
        current.update(status_payload)
        current["movie_id"] = movie_id

        if previous.get("status") in TERMINAL and current.get("status") != previous["status"]:
            raise ValueError("terminal job status cannot move backwards")

        self.jobs[movie_id] = current
        return dict(current)
