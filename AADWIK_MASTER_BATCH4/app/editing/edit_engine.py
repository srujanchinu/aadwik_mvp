from dataclasses import dataclass, field

@dataclass
class VideoClip:
    clip_id: str
    source: str
    start: float
    duration: float
    scene_number: int | None = None
    shot_id: str | None = None

@dataclass
class EditTimeline:
    fps: float = 24.0
    width: int = 1920
    height: int = 1080
    clips: list = field(default_factory=list)

    def add(self, clip):
        if clip.start < 0 or clip.duration <= 0:
            raise ValueError("Video clip timing is invalid")
        self.clips.append(clip)
        return clip

    @property
    def duration(self):
        return max((c.start + c.duration for c in self.clips), default=0.0)

def build_edit_timeline(shots, fps=24.0, width=1920, height=1080):
    timeline = EditTimeline(fps=fps, width=width, height=height)
    cursor = 0.0
    for shot in shots:
        duration = float(shot.get("duration", shot.get("duration_seconds", 1.0)))
        clip = VideoClip(
            clip_id=str(shot.get("shot_id") or f"shot_{len(timeline.clips)+1:04d}"),
            source=str(shot.get("source") or ""),
            start=cursor,
            duration=duration,
            scene_number=shot.get("scene_number"),
            shot_id=shot.get("shot_id"),
        )
        timeline.add(clip)
        cursor += duration
    return timeline

def build_assembly_manifest(video, audio, subtitles=None):
    return {
        "video": video,
        "audio_duration": audio.duration if hasattr(audio, "duration") else 0,
        "subtitles": subtitles or [],
        "assembly_ready": bool(video),
    }
