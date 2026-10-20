from dataclasses import dataclass
from typing import Dict

@dataclass
class MovieState:
    movie_id: str
    status: str = "queued"
    progress: float = 0.0
    current_step: str = ""
    output_path: str = ""
    error: str = ""

class MovieStateAdapter:
    def __init__(self):
        self.states: Dict[str, MovieState] = {}

    def get(self, movie_id):
        return self.states.get(movie_id)

    def apply(self, update):
        state = self.states.get(update.movie_id)
        if not state:
            state = MovieState(update.movie_id)
            self.states[update.movie_id] = state
        state.status = update.status
        state.progress = max(0.0, min(1.0, update.progress))
        state.current_step = update.step
        state.output_path = update.output_path
        state.error = update.errors[0] if update.errors else ""
        return state
