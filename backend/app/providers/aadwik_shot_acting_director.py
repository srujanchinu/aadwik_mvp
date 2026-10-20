import json
from pathlib import Path

# STEP 8F — Shot-level Acting Director
# Converts cinematic shot intent into deterministic reusable character actions.

DEFAULT_ACTIONS = {
    "establishing": "idle",
    "discovery": "look",
    "journey": "walk",
    "companion": "look",
    "revelation": "look",
    "conflict": "threaten",
    "choice": "look",
    "resolution": "reach",
    "transformation": "look",
    "ending": "walk",
    "final_image": "idle",
}

CHARACTER_ACTION_OVERRIDES = {
    "tara": {
        "discovery": "look",
        "journey": "walk",
        "choice": "look",
        "resolution": "reach",
        "final_image": "idle",
    },
    "guardian": {
        "companion": "injured",
        "journey": "injured",
        "conflict": "injured",
        "resolution": "look",
    },
    "shadow_creature": {
        "conflict": "threaten",
        "revelation": "threaten",
    },
}

def choose_action(character_id, event_type):
    char = character_id.replace("char_", "").replace("_v1", "")
    return CHARACTER_ACTION_OVERRIDES.get(char, {}).get(
        event_type, DEFAULT_ACTIONS.get(event_type, "idle")
    )

def direct_shot(shot):
    event_type=shot.get("event_type", shot.get("scene_type", "establishing"))
    chars=shot.get("characters", [])
    directives=[]
    for c in chars:
        cid=c if isinstance(c,str) else c.get("id", c.get("character_id",""))
        if not cid:
            continue
        directives.append({
            "character_id": cid,
            "action": choose_action(cid,event_type),
            "emotion": shot.get("emotion","neutral"),
            "start_frame": shot.get("start_frame",1),
            "end_frame": shot.get("end_frame",32),
        })
    result=dict(shot)
    result["acting_directives"]=directives
    result["acting_director_locked"]=True
    return result

def direct_job(job):
    result=dict(job)
    result["shots"]=[direct_shot(s) for s in job.get("shots",[])]
    result["acting_system"]={
        "schema":"aadwik-acting-director-1.0",
        "deterministic":True,
        "story_driven":True,
        "identity_locked":True,
    }
    return result

def save_job(job,path):
    Path(path).write_text(json.dumps(job,indent=2),encoding="utf-8")
