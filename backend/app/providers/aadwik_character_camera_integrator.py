import json
from pathlib import Path

# STEP 8G — Character + Acting + Camera integration.
# Produces a deterministic shot payload ready for the Blender consumer.

ASSET_ROOTS={
 "char_tara_v1":"CHAR_TARA_ROOT",
 "char_guardian_v1":"CHAR_GUARDIAN_ROOT",
 "char_shadow_creature_v1":"CHAR_SHADOW_ROOT",
 "prop_blue_star_v1":"PROP_BLUE_STAR",
}

SAFE_ACTIONS={
 "tara":{"discovery":"look","journey":"walk","choice":"look","resolution":"reach","final_image":"idle","conflict":"look"},
 "guardian":{"companion":"injured","journey":"injured","conflict":"injured","resolution":"look"},
 "shadow_creature":{"conflict":"threaten","revelation":"threaten"},
}

def action_for(character_id,event_type):
    c=character_id.replace("char_","").replace("_v1","")
    return SAFE_ACTIONS.get(c,{}).get(event_type,"idle")

def integrate_shot(shot):
    result=dict(shot)
    event=shot.get("event_type",shot.get("scene_type","establishing"))
    chars=shot.get("characters",[])
    directives=[]
    for c in chars:
        cid=c if isinstance(c,str) else c.get("id",c.get("character_id",""))
        if cid not in ASSET_ROOTS:
            continue
        directives.append({
            "character_id":cid,
            "asset_id":cid,
            "blender_root":ASSET_ROOTS[cid],
            "action":action_for(cid,event),
            "emotion":shot.get("emotion","neutral"),
        })
    result["asset_bindings"]=directives
    result["camera_binding"]={
        "camera_id":shot.get("camera_id",f"CAM_{shot.get('shot_id','UNKNOWN')}"),
        "framing":shot.get("framing","medium"),
        "lens_mm":shot.get("lens_mm",50),
        "movement":shot.get("camera_movement","static"),
        "camera_locked":True,
    }
    result["production_ready"]=True
    return result

def integrate_job(job):
    out=dict(job)
    out["shots"]=[integrate_shot(s) for s in job.get("shots",[])]
    out["integration"]={
        "schema":"aadwik-character-acting-camera-1.0",
        "asset_identity_locked":True,
        "acting_locked":True,
        "camera_locked":True,
    }
    return out

def save_job(job,path):
    Path(path).write_text(json.dumps(job,indent=2),encoding="utf-8")
