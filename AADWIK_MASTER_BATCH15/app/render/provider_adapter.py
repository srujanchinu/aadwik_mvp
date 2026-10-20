from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class ProviderAdapterResult:
    success: bool
    output_path: str = ""
    provider: str = ""
    error: str = ""
    metadata: Dict[str, Any] = None

class ProviderAdapter:
    """Normalizes provider invocation without binding Aadwik to one renderer."""

    def __init__(self, provider):
        self.provider = provider

    def generate(self, prompt: str, output_path: str, **kwargs):
        try:
            result = self.provider.generate_video(
                prompt, output_path, **kwargs
            )
            return ProviderAdapterResult(
                success=True,
                output_path=str(result or output_path),
                provider=type(self.provider).__name__,
                metadata=kwargs,
            )
        except Exception as exc:
            return ProviderAdapterResult(
                success=False,
                provider=type(self.provider).__name__,
                error=str(exc),
                metadata=kwargs,
            )
