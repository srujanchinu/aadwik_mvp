
from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict

def build_production_payload(plan: Dict[str,Any]) -> Dict[str,Any]:
    """Create the canonical renderer payload without generating video."""
    scenes=[]
    for scene in plan.get("scenes",[]):
        scenes.append({
            "scene_number":scene.get("scene_number"),
            "scene_id":scene.get("id"),
            "title":scene.get("title"),
            "type":scene.get("type"),
            "story_text":scene.get("story_text",""),
            "location":scene.get("locked_location",scene.get("location","story_world")),
            "characters":scene.get("locked_characters",scene.get("characters",[])),
            "props":scene.get("locked_props",[]),
            "emotion":scene.get("emotion","neutral"),
            "shots":scene.get("shots",[]),
            "continuity":scene.get("continuity",{
                "character_lock":True,
                "world_lock":True,
                "prop_lock":True
            })
        })
    payload={
        "schema_version":"aadwik-production-1.0",
        "title":plan.get("title","Aadwik Production"),
        "story":plan.get("story",""),
        "metadata":plan.get("metadata",{}),
        "character_lock":plan.get("character_lock",{}),
        "world_lock":plan.get("world_lock",{}),
        "prop_lock":plan.get("prop_lock",{}),
        "scenes":scenes,
        "shot_plan":plan.get("shot_plan",{}),
        "production_summary":plan.get("production_summary",{})
    }
    return payload

def save_production_payload(plan:Dict[str,Any], output_path) -> str:
    path=Path(output_path)
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=build_production_payload(plan)
    path.write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding="utf-8")
    return str(path)

def load_production_payload(path) -> Dict[str,Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
