from dataclasses import dataclass, field

@dataclass
class AudioClip:
    clip_id: str
    kind: str
    start: float
    duration: float
    source: str = ""
    volume: float = 1.0

@dataclass
class AudioTimeline:
    sample_rate: int = 48000
    clips: list = field(default_factory=list)

    def add(self, clip):
        if clip.start < 0 or clip.duration <= 0:
            raise ValueError("Audio clip timing is invalid")
        self.clips.append(clip)
        return clip

    @property
    def duration(self):
        return max((c.start + c.duration for c in self.clips), default=0.0)

def plan_audio(dialogue=None, music=None, sfx=None):
    timeline = AudioTimeline()
    for group, kind in ((dialogue or [], "dialogue"), (music or [], "music"), (sfx or [], "sfx")):
        for i, item in enumerate(group):
            timeline.add(AudioClip(
                clip_id=str(item.get("clip_id") or f"{kind}_{i+1:04d}"),
                kind=kind,
                start=float(item.get("start", 0)),
                duration=float(item.get("duration", 1)),
                source=str(item.get("source", "")),
                volume=float(item.get("volume", 1.0)),
            ))
    return timeline

def validate_audio(timeline, video_duration, tolerance=0.25):
    return abs(timeline.duration - float(video_duration)) <= tolerance or timeline.duration == 0
