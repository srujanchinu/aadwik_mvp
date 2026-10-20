from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class BridgeResult:
    success: bool
    status: str
    output_path: str = ""
    errors: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class RenderBridge:
    """Adapter boundary for connecting Aadwik movie generation to render execution.

    It accepts an injected renderer so integration can be tested without
    launching Blender/FFmpeg.
    """

    def __init__(self, renderer):
        self.renderer = renderer

    def execute(self, prompt: str, output_path: str, **kwargs) -> BridgeResult:
        try:
            result = self.renderer.generate_video(
                prompt, output_path, **kwargs
            )
            path = str(result or output_path)
            return BridgeResult(True, "generated", path,
                                metadata={"provider": type(self.renderer).__name__})
        except Exception as exc:
            return BridgeResult(False, "failed", "",
                                [str(exc)],
                                {"provider": type(self.renderer).__name__})
