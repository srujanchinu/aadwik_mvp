import json
from pathlib import Path

SCHEMA="aadwik-dialogue-1.0"

class DialogueLine:
    def __init__(self,line_id,character_id,text,scene_id,shot_id,
                 start_sec=0.0,duration_sec=2.0,language="en-IN",
                 emotion="natural"):
        self.line_id=line_id
        self.character_id=character_id
        self.text=text
        self.scene_id=scene_id
        self.shot_id=shot_id
        self.start_sec=float(start_sec)
        self.duration_sec=float(duration_sec)
        self.language=language
        self.emotion=emotion

    def to_dict(self):
        return {
            "schema":SCHEMA,"line_id":self.line_id,
            "character_id":self.character_id,"text":self.text,
            "scene_id":self.scene_id,"shot_id":self.shot_id,
            "start_sec":self.start_sec,"duration_sec":self.duration_sec,
            "language":self.language,"emotion":self.emotion
        }

class DialogueTimeline:
    def __init__(self):
        self.lines=[]

    def add(self,line):
        if any(x.line_id==line.line_id for x in self.lines):
            raise ValueError("duplicate dialogue line id")
        if line.start_sec < 0 or line.duration_sec <= 0:
            raise ValueError("invalid dialogue timing")
        self.lines.append(line)

    def validate(self):
        issues=[]
        last=-1
        for x in self.lines:
            if x.start_sec < last:
                issues.append("dialogue timeline is not chronological")
            last=x.start_sec
        return {"valid":not issues,"issues":issues,
                "line_count":len(self.lines),
                "schema":SCHEMA,
                "lines":[x.to_dict() for x in self.lines]}

def save_timeline(timeline,path):
    Path(path).write_text(json.dumps(timeline.validate(),indent=2),encoding="utf-8")
