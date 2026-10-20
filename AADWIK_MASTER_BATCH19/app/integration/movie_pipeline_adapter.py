from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class PipelineUpdate:
    movie_id: str
    status: str
    progress: float
    step: str
    output_path: str = ""
    errors: list = field(default_factory=list)

class MoviePipelineAdapter:
    def __init__(self, renderer, event_stream=None):
        self.renderer = renderer
        self.event_stream = event_stream

    def _emit(self, movie_id, step, status, progress, message=""):
        if self.event_stream:
            self.event_stream.emit(movie_id, step, status, progress, message)

    def generate(self, movie_id: str, prompt: str, output_path: str,
                 aspect_ratio: str = "16:9", style: Optional[str] = None,
                 **kwargs) -> PipelineUpdate:
        self._emit(movie_id, "generation", "running", 0.1, "Generation started")
        try:
            options: Dict[str, Any] = dict(kwargs)
            options["aspect_ratio"] = aspect_ratio
            if style:
                options["style"] = style
            self._emit(movie_id, "render", "running", 0.5, "Renderer invoked")
            result = self.renderer.generate_video(prompt, output_path, **options)
            final_path = str(result or output_path)
            self._emit(movie_id, "generation", "complete", 1.0, "Generation complete")
            return PipelineUpdate(movie_id, "completed", 1.0, "generation", final_path)
        except Exception as exc:
            self._emit(movie_id, "generation", "failed", 1.0, str(exc))
            return PipelineUpdate(movie_id, "failed", 1.0, "generation",
                                  errors=[str(exc)])

class SafeGenerationController:
    def __init__(self, enabled=True):
        self.enabled = bool(enabled)

    def can_generate(self):
        return self.enabled

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True
