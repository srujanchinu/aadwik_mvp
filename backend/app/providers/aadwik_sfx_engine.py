import json
from pathlib import Path
SCHEMA="aadwik-sfx-plan-1.0"
class SFXCue:
    def __init__(self,sfx_id,scene_id,shot_id,start_sec,duration_sec,event):
        self.sfx_id=sfx_id; self.scene_id=scene_id; self.shot_id=shot_id
        self.start_sec=float(start_sec); self.duration_sec=float(duration_sec); self.event=event
    def to_dict(self):
        return {"schema":SCHEMA,"sfx_id":self.sfx_id,"scene_id":self.scene_id,
                "shot_id":self.shot_id,"start_sec":self.start_sec,
                "duration_sec":self.duration_sec,"event":self.event}
class SFXTimeline:
    def __init__(self): self.cues=[]
    def add(self,c): self.cues.append(c)
    def validate(self):
        bad=[c.sfx_id for c in self.cues if c.start_sec<0 or c.duration_sec<=0]
        return {"valid":not bad,"issues":bad,"cue_count":len(self.cues),"schema":SCHEMA,
                "cues":[c.to_dict() for c in self.cues]}
def save_timeline(t,p): Path(p).write_text(json.dumps(t.validate(),indent=2),encoding="utf-8")
