import json
from pathlib import Path
SCHEMA="aadwik-ambience-plan-1.0"
class AmbienceCue:
    def __init__(self,cue_id,world_id,start_sec,duration_sec,environment,level=.4):
        self.cue_id=cue_id; self.world_id=world_id; self.start_sec=float(start_sec)
        self.duration_sec=float(duration_sec); self.environment=environment; self.level=float(level)
    def to_dict(self):
        return {"schema":SCHEMA,"cue_id":self.cue_id,"world_id":self.world_id,
                "start_sec":self.start_sec,"duration_sec":self.duration_sec,
                "environment":self.environment,"level":self.level}
class AmbienceTimeline:
    def __init__(self): self.cues=[]
    def add(self,c): self.cues.append(c)
    def validate(self):
        bad=[c.cue_id for c in self.cues if c.duration_sec<=0 or not 0<=c.level<=1]
        return {"valid":not bad,"issues":bad,"cue_count":len(self.cues),"schema":SCHEMA,
                "cues":[c.to_dict() for c in self.cues]}
def save_timeline(t,p): Path(p).write_text(json.dumps(t.validate(),indent=2),encoding="utf-8")
