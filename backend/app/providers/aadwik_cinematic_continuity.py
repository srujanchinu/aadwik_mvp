import json
from pathlib import Path

LOCKED_WORLDS={
 "world_forest_moonlit_v1",
 "world_ancient_tree_v1",
 "world_glowing_river_v1",
 "world_ancient_temple_v1",
 "world_village_festival_v1",
 "world_village_home_v1",
 "world_magical_forest_v1",
}
LOCKED_CHARACTERS={
 "char_tara_v1","char_guardian_v1","char_shadow_creature_v1"
}
LOCKED_PROPS={"prop_blue_star_v1"}

def validate_cinematic_continuity(shots):
    issues=[]
    cameras=[]
    for i,s in enumerate(shots,1):
        world=s.get("world_id")
        chars=s.get("character_ids",[])
        props=s.get("prop_ids",[])
        camera=s.get("camera",{})
        acting=s.get("acting",{})

        if world not in LOCKED_WORLDS:
            issues.append(f"shot_{i}: invalid locked world")
        for x in chars:
            if x not in LOCKED_CHARACTERS:
                issues.append(f"shot_{i}: invalid character {x}")
        for x in props:
            if x not in LOCKED_PROPS:
                issues.append(f"shot_{i}: invalid prop {x}")

        if not camera.get("position") or not camera.get("target"):
            issues.append(f"shot_{i}: incomplete camera")
        if not acting:
            issues.append(f"shot_{i}: missing acting directives")

        cameras.append(tuple(camera.get("position",[])))

    # Cinematic continuity requires deliberate camera changes rather than
    # accidental identical framing for every shot.
    if len(set(cameras)) < 2:
        issues.append("camera: no shot-to-shot movement/change detected")

    return {
        "valid":not issues,
        "issues":issues,
        "shot_count":len(shots),
        "world_locked":all(s.get("world_id") in LOCKED_WORLDS for s in shots),
        "characters_locked":all(x in LOCKED_CHARACTERS for s in shots for x in s.get("character_ids",[])),
        "props_locked":all(x in LOCKED_PROPS for s in shots for x in s.get("prop_ids",[])),
        "camera_continuity":len(set(cameras)) >= 2,
    }

def save_report(report,path):
    Path(path).write_text(json.dumps(report,indent=2),encoding="utf-8")
