import json
from pathlib import Path

SCHEMA="aadwik-music-plan-1.0"

class MusicCue:
    def __init__(self,cue_id,scene_id,start_sec,duration_sec,mood,intensity=0.5):
        self.cue_id=cue_id; self.scene_id=scene_id
        self.start_sec=float(start_sec); self.duration_sec=float(duration_sec)
        self.mood=mood; self.intensity=float(intensity)
    def to_dict(self):
        return {"schema":SCHEMA,"cue_id":self.cue_id,"scene_id":self.scene_id,
                "start_sec":self.start_sec,"duration_sec":self.duration_sec,
                "mood":self.mood,"intensity":self.intensity}

class MusicTimeline:
    def __init__(self): self.cues=[]
    def add(self,cue):
        if any(x.cue_id==cue.cue_id for x in self.cues): raise ValueError("duplicate cue")
        self.cues.append(cue)
    def validate(self):
        issues=[]
        for x in self.cues:
            if x.duration_sec<=0 or x.start_sec<0: issues.append(x.cue_id)
            if not 0<=x.intensity<=1: issues.append(x.cue_id)
        return {"valid":not issues,"issues":issues,"cue_count":len(self.cues),
                "schema":SCHEMA,"cues":[x.to_dict() for x in self.cues]}

def save_timeline(t,p): Path(p).write_text(json.dumps(t.validate(),indent=2),encoding="utf-8")
