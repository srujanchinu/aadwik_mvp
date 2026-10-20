import json
from pathlib import Path

# STEP 9E — Multi-shot world continuity validator.
# Ensures consecutive shots keep the same locked world unless an intentional
# world transition is explicitly declared.

def validate_sequence(shots):
    if not shots:
        raise ValueError("Sequence contains no shots")

    issues=[]
    previous_world=None
    previous_characters=None
    previous_props=None

    for i,shot in enumerate(shots,1):
        world=shot.get("world_id")
        chars=tuple(sorted(shot.get("character_ids",[])))
        props=tuple(sorted(shot.get("prop_ids",[])))

        if not world:
            issues.append(f"shot_{i}: missing world_id")

        if shot.get("continuity_break") is not True and previous_world and world != previous_world:
            issues.append(f"shot_{i}: unexpected world change {previous_world} -> {world}")

        if shot.get("continuity_break") is not True:
            # Characters/props may enter or leave intentionally; identity is
            # checked by locked IDs, not by requiring identical cast every shot.
            for aid in chars + props:
                if not aid.endswith("_v1"):
                    issues.append(f"shot_{i}: unlocked asset id {aid}")

        previous_world=world
        previous_characters=chars
        previous_props=props

    return {"valid":not issues,"issues":issues,"shot_count":len(shots)}

def lock_sequence(shots):
    result=[]
    for shot in shots:
        s=dict(shot)
        s["world_continuity_locked"]=True
        s["world_instance_id"]=s.get("world_id")
        result.append(s)
    return result

def save_report(report,path):
    Path(path).write_text(json.dumps(report,indent=2),encoding="utf-8")
