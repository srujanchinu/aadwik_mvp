
from __future__ import annotations
from typing import Any, Dict, List

def _action_for(scene: Dict[str,Any]) -> str:
    return scene.get("story_text") or scene.get("title","")

def build_shot_plan(plan: Dict[str,Any]) -> Dict[str,Any]:
    """Convert locked story events into explicit cinematic shots.
    This is a shot-specification layer; it does not render video.
    """
    scenes=[]
    shot_total=0
    for scene in plan.get("scenes",[]):
        title=scene.get("title","Untitled Scene")
        loc=scene.get("locked_location",scene.get("location","story_world"))
        chars=scene.get("locked_characters",scene.get("characters",[]))
        props=scene.get("locked_props",[])
        emotion=scene.get("emotion","neutral")
        kind=scene.get("type","event")
        action=_action_for(scene)

        if kind in ("establishing","journey","reveal","transformation","ending"):
            shot_specs=[
                ("wide_establishing","wide","24mm","slow crane/dolly","Establish the environment before the action.","cinematic environmental composition"),
                ("subject_action","medium","50mm","tracking","Show the characters performing the story action.","clear character blocking and readable action"),
                ("emotional_detail","close_up","85mm","slow push_in","Capture the emotional consequence of the moment.","expressive face/creature detail"),
            ]
        elif kind in ("discovery","companion","revelation","conflict","choice","resolution"):
            shot_specs=[
                ("context","wide","28mm","slow dolly","Show where the event happens and who is present.","strong foreground/midground/background depth"),
                ("action","medium","50mm","tracking_or_handheld","Show the central story action clearly.","dynamic blocking"),
                ("reaction","close_up","85mm","slow push_in","Show the key character reaction.","emotion-first framing"),
            ]
        elif kind=="final_image":
            shot_specs=[
                ("memory_wide","wide","35mm","slow pull_back","Show the quiet final environment.","peaceful composition"),
                ("final_detail","close_up","100mm","locked_off","Hold on the important final visual object.","hero prop detail"),
            ]
        else:
            shot_specs=[
                ("establishing","wide","28mm","slow dolly","Establish the scene.","cinematic depth"),
                ("action","medium","50mm","tracking","Advance the story event.","clear action"),
                ("reaction","close_up","85mm","push_in","Show emotional response.","emotion-first framing"),
            ]

        shots=[]
        for idx,(stype,framing,lens,movement,action_text,composition) in enumerate(shot_specs,1):
            shots.append({
                "shot_id":f"{scene.get('id','scene')}_shot_{idx:02d}",
                "scene_number":scene.get("scene_number"),
                "shot_number":idx,
                "shot_type":stype,
                "framing":framing,
                "lens":lens,
                "camera_movement":movement,
                "camera_direction":"follow story action; preserve screen direction",
                "location":loc,
                "characters":chars,
                "props":props,
                "primary_action":action_text,
                "story_context":action,
                "emotion":emotion,
                "composition":composition,
                "lighting":"motivated by location, time and story emotion",
                "depth":"foreground + subject + background layers",
                "continuity":{
                    "character_lock":True,
                    "world_lock":True,
                    "prop_lock":True,
                    "screen_direction_lock":True
                },
                "negative_constraints":[
                    "do not redesign locked characters",
                    "do not change locked clothing",
                    "do not replace the location with a generic set",
                    "do not introduce unrelated characters or props",
                    "do not make the shot static unless specified"
                ]
            })
        scenes.append(dict(scene, shots=shots, shot_count=len(shots),
                           shot_plan_status="PLANNED"))
        shot_total += len(shots)

    out=dict(plan)
    out["scenes"]=scenes
    out["shot_plan"]={
        "version":"1.0",
        "status":"complete",
        "scene_count":len(scenes),
        "shot_count":shot_total,
        "rules":["story action drives shots","locked assets are mandatory","camera changes serve narrative"]
    }
    out["production_summary"]=dict(out.get("production_summary",{}))
    out["production_summary"]["shot_count"]=shot_total
    out["production_summary"]["shot_plan_complete"]=True
    return out

def create_shot_plan(plan,**kwargs): return build_shot_plan(plan)
def plan_shots(plan,**kwargs): return build_shot_plan(plan)
class CinematicShotPlanner:
    def build(self,plan,**kwargs): return build_shot_plan(plan,**kwargs)
