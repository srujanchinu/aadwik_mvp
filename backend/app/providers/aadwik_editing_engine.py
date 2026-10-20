import json
from pathlib import Path

SCHEMA="aadwik-edit-timeline-1.0"

class Clip:
    def __init__(self,clip_id,shot_id,start,duration,source):
        self.clip_id=clip_id; self.shot_id=shot_id
        self.start=float(start); self.duration=float(duration); self.source=source
    def to_dict(self):
        return {"clip_id":self.clip_id,"shot_id":self.shot_id,
                "start":self.start,"duration":self.duration,"source":self.source}

class Timeline:
    def __init__(self): self.clips=[]; self.transitions=[]; self.overlays=[]
    def add_clip(self,c):
        if any(x.clip_id==c.clip_id for x in self.clips): raise ValueError("duplicate clip")
        self.clips.append(c)
    def add_transition(self,a,b,kind="cut"): self.transitions.append({"from":a,"to":b,"type":kind})
    def add_overlay(self,kind,text,start,duration): self.overlays.append(
        {"type":kind,"text":text,"start":float(start),"duration":float(duration)})
    def validate(self):
        issues=[]
        if not self.clips: issues.append("no clips")
        for c in self.clips:
            if c.start<0 or c.duration<=0: issues.append(c.clip_id)
        ordered=sorted(self.clips,key=lambda x:x.start)
        for a,b in zip(ordered,ordered[1:]):
            if a.start+a.duration>b.start: issues.append("overlapping clips")
        return {"valid":not issues,"issues":issues,"schema":SCHEMA,
                "clip_count":len(self.clips),"transition_count":len(self.transitions),
                "overlay_count":len(self.overlays)}
def save(t,p): Path(p).write_text(json.dumps(t.validate(),indent=2),encoding="utf-8")
