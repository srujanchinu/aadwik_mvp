from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class MovieGenerationRequest:
    movie_id: str
    prompt: str
    output_path: str
    aspect_ratio: str = "16:9"
    style: str = ""
    options: Dict[str, Any] = None

class MovieGenerationAdapter:
    """Converts an API/movie request into the stable RenderBridge contract."""

    def __init__(self, bridge):
        self.bridge = bridge

    def generate(self, request: MovieGenerationRequest):
        options = dict(request.options or {})
        if request.style:
            options["style"] = request.style
        options["aspect_ratio"] = request.aspect_ratio
        result = self.bridge.execute(
            request.prompt, request.output_path, **options
        )
        return result
