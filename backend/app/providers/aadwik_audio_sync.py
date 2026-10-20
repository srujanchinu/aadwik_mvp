import json
from pathlib import Path
SCHEMA="aadwik-audio-sync-1.0"
def validate_sync(dialogue,music,sfx,ambience,shot_duration):
    tracks=[("dialogue",dialogue),("music",music),("sfx",sfx),("ambience",ambience)]
    issues=[]
    for name,items in tracks:
        for x in items:
            start=float(x.get("start_sec",0)); dur=float(x.get("duration_sec",0))
            if start<0 or dur<=0 or start+dur>shot_duration+1e-6:
                issues.append(f"{name}:{x.get('id','unknown')}")
    return {"valid":not issues,"issues":issues,"schema":SCHEMA,
            "tracks":{"dialogue":len(dialogue),"music":len(music),
                      "sfx":len(sfx),"ambience":len(ambience)}}
def save_report(r,p): Path(p).write_text(json.dumps(r,indent=2),encoding="utf-8")
