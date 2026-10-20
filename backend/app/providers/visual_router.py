
from __future__ import annotations
import os

class VisualRouter:
    """Single provider entry point. Local is the safe default."""
    def __init__(self, mode=None):
        self.mode=(mode or os.getenv("AADWIK_VIDEO_PROVIDER","local")).lower().strip()

    def generate_video(self, *, prompt, output_path, aspect_ratio="16:9", style="", production_plan=None, **kwargs):
        if self.mode in {"veo","ai","google"}:
            from app.providers.veo_provider import VeoProvider
            provider=VeoProvider()
        else:
            from app.providers.local_video_provider import LocalVideoProvider
            provider=LocalVideoProvider()
        try:
            return provider.generate_video(prompt=prompt, output_path=output_path,
                                           aspect_ratio=aspect_ratio, style=style,
                                           production_plan=production_plan, **kwargs)
        except TypeError:
            return provider.generate_video(prompt=prompt, output_path=output_path,
                                           aspect_ratio=aspect_ratio, style=style, **kwargs)

    def create_provider(self):
        if self.mode in {"veo","ai","google"}:
            from app.providers.veo_provider import VeoProvider
            return VeoProvider()
        from app.providers.local_video_provider import LocalVideoProvider
        return LocalVideoProvider()

visual_router=VisualRouter()
video_provider=visual_router
