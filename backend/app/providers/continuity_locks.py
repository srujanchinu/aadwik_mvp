
from __future__ import annotations
from typing import Any, Dict, List
import re

def _id(text:str)->str:
    return re.sub(r"[^a-z0-9]+","_",text.lower()).strip("_")

def build_locks(plan:Dict[str,Any])->Dict[str,Any]:
    scenes=plan.get("scenes",[])
    chars=plan.get("character_lock",{}).get("characters",[])
    character_lock=[]
    for c in chars:
        character_lock.append({
            "id":c.get("id") or _id(c.get("name","character")),
            "name":c.get("name","Character"),
            "type":c.get("type","unknown"),
            "role":c.get("role","supporting"),
            "visual_identity":{
                "appearance":c.get("appearance","consistent stylized cinematic 3D character"),
                "face_lock":True,
                "body_lock":True,
                "clothing_lock":True,
                "color_palette_lock":True
            },
            "continuity_rules":["same identity in every scene","same proportions","same clothing unless explicitly changed"]
        })

    locations={}
    for s in scenes:
        loc=s.get("location","story_world")
        if loc not in locations:
            locations[loc]={
                "id":_id(loc),"name":loc.replace("_"," ").title(),
                "environment_style":"cinematic stylized 3D",
                "layout_lock":True,"lighting_identity":True,"color_identity":True,
                "continuity_rules":["same major landmarks","same environmental identity across shots"]
            }

    props={}
    for s in scenes:
        for prop in s.get("props",[]):
            pid=prop.get("id") if isinstance(prop,dict) else _id(str(prop))
            name=prop.get("name",pid) if isinstance(prop,dict) else str(prop)
            props[pid]={
                "id":pid,"name":name,
                "visual_identity":"distinctive cinematic 3D prop",
                "shape_lock":True,"material_lock":True,"color_lock":True,
                "continuity_rules":["same object identity whenever it reappears"]
            }

    return {
        "character_lock":{"count":len(character_lock),"characters":character_lock},
        "world_lock":{"count":len(locations),"locations":list(locations.values())},
        "prop_lock":{"count":len(props),"props":list(props.values())}
    }

def apply_locks(plan:Dict[str,Any])->Dict[str,Any]:
    locks=build_locks(plan)
    plan=dict(plan)
    plan["character_lock"]=locks["character_lock"]
    plan["world_lock"]=locks["world_lock"]
    plan["prop_lock"]=locks["prop_lock"]
    for s in plan.get("scenes",[]):
        s=dict(s)
        s["locked_characters"]=s.get("characters",[])
        s["locked_location"]=s.get("location","story_world")
        s["locked_props"]=[x.get("id",x) if isinstance(x,dict) else x for x in s.get("props",[])]
        s["visual_continuity"]="LOCKED"
        s["production_directive"]="Use the locked character, world and prop identities; do not redesign recurring assets."
        # Keep scene-local copies so downstream renderers can consume one scene independently.
        s["asset_references"]={
            "characters":s["locked_characters"],
            "location":s["locked_location"],
            "props":s["locked_props"]
        }
    plan["scenes"]=[dict(x) for x in plan.get("scenes",[])]
    plan["production_summary"]=dict(plan.get("production_summary",{}))
    plan["production_summary"].update({
        "character_lock_count":len(locks["character_lock"]["characters"]),
        "world_lock_count":len(locks["world_lock"]["locations"]),
        "prop_lock_count":len(locks["prop_lock"]["props"]),
        "continuity_locked":True
    })
    return plan

def lock_production_assets(plan:Dict[str,Any])->Dict[str,Any]:
    return apply_locks(plan)
