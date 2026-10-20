from dataclasses import dataclass, field

@dataclass
class QualityCheck:
    name: str
    passed: bool
    message: str
    metrics: dict = field(default_factory=dict)

def check_video_spec(video):
    required = ("path","width","height","fps","duration")
    missing = [k for k in required if k not in video]
    if missing:
        return QualityCheck("video_spec",False,"Missing video fields",{"missing":missing})
    ok = video["width"] > 0 and video["height"] > 0 and video["fps"] > 0 and video["duration"] > 0
    return QualityCheck("video_spec",ok,"Video specification valid" if ok else "Invalid video specification")

def check_timeline(timeline):
    ok = timeline.duration >= 0 and all(c.duration > 0 for c in timeline.clips)
    return QualityCheck("edit_timeline",ok,"Edit timeline valid" if ok else "Invalid edit timeline")

def run_production_quality(video, timeline):
    checks=[check_video_spec(video),check_timeline(timeline)]
    return {
        "passed": all(c.passed for c in checks),
        "score": (sum(c.passed for c in checks)/len(checks))*100,
        "checks":[c.__dict__ for c in checks],
    }
