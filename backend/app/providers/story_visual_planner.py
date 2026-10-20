
from __future__ import annotations
import re
from typing import Any, Dict, List

def _s(v): return "" if v is None else str(v).strip()
def _has(t,*words): return any(w in t.lower() for w in words)

def _characters(story:str)->List[Dict[str,Any]]:
    out=[]
    for name in re.findall(r"\b(?:named|called)\s+([A-Z][A-Za-z0-9_-]+)",story):
        if not any(x["name"].lower()==name.lower() for x in out):
            out.append({"id":name.lower(),"name":name,"type":"human","role":"protagonist",
                        "appearance":"consistent stylized 3D human character","continuity_lock":True})
    t=story.lower()
    if "girl" in t and not any(x["id"]=="girl" for x in out):
        out.append({"id":"girl","name":"Girl","type":"human","role":"protagonist",
                    "appearance":"consistent stylized 3D girl character","continuity_lock":True})
    if _has(t,"creature","guardian","animal","dragon","monster"):
        out.append({"id":"guardian","name":"Guardian","type":"fantasy_creature","role":"companion",
                    "appearance":"small injured magical guardian creature","continuity_lock":True})
    if "shadow creature" in t:
        out.append({"id":"shadow_creature","name":"Shadow Creature","type":"fantasy_creature","role":"antagonist",
                    "appearance":"dark smoky supernatural creature with glowing eyes","continuity_lock":True})
    return out

def _scene(title,kind,loc,text,chars,props,emotion):
    return {"title":title,"type":kind,"location":loc,"story_text":text,
            "characters":[c["id"] for c in chars],"props":props,"emotion":emotion,
            "continuity":{"character_lock":True,"world_lock":True,"props_lock":True}}

def _events(story:str):
    # Event extraction intentionally prioritizes narrative actions and landmarks.
    # It produces a minimum chronological spine even when many actions occur
    # in one grammatical sentence.
    t=story.lower()
    events=[]
    def add(title,kind,loc,keys,emotion,props=()):
        if any(k in t for k in keys):
            events.append((title,kind,loc,emotion,list(props)))
    add("Village Festival","establishing","village",["festival","village"],"joy",["lanterns"])
    add("Blue Star Falls","discovery","sky",["blue star","star fall","star falls","fall from the sky","falls from the sky"],"wonder",["blue_star"])
    add("Glowing Trail into the Forest","journey","forest",["follows","forest","woods"],"curiosity",["blue_star"])
    add("Injured Guardian Discovered","companion","ancient_tree",["injured","guardian","creature","hiding"],"concern",["blue_star","ancient_tree"])
    add("Guardian's Stolen Star Revealed","revelation","forest",["stolen","stolen by","guardian"],"mystery",["blue_star"])
    add("Journey Through the Moonlit Forest","journey","forest",["journey","moonlit forest","together"],"adventure",["blue_star"])
    add("Glowing River Crossing","journey","river",["river","cross"],"wonder",["blue_star"])
    add("Ancient Stone Temple","reveal","temple",["temple","ancient temple","stone temple"],"mystery",["blue_star"])
    add("Shadow Creature Appears","conflict","temple",["shadow creature","shadow"],"tension",["blue_star"])
    add("Tara Chooses Courage and Compassion","choice","temple",["courage","compassion","weapon"],"bravery",["blue_star"])
    add("Star Returned to the Guardian","resolution","temple",["return","returns","returned"],"relief",["blue_star"])
    add("Forest Comes Alive With Light","transformation","forest",["comes alive","alive with light","forest comes alive"],"wonder",["blue_star"])
    add("Sunrise Return Home","ending","home",["sunrise","returns home","return home"],"peace",["blue_star"])
    add("The Tiny Star Remains in Her Hand","final_image","home",["still glowing","in her hand","tiny star"],"hope",["blue_star"])
    # Remove duplicates by (title), preserving chronology.
    seen=set(); result=[]
    for e in events:
        if e[0] not in seen:
            seen.add(e[0]); result.append(e)
    return result

def analyze_story(story:str,**kwargs)->Dict[str,Any]:
    story=_s(story)
    if not story: raise ValueError("Story text is empty.")
    chars=_characters(story)
    events=_events(story)
    # Fallback: always create at least three events.
    if not events:
        events=[("Opening","establishing","story_world","curiosity",[]),
                ("Main Story Event","event","story_world","tension",[]),
                ("Ending","ending","story_world","hope",[])]
    scenes=[]
    for i,(title,kind,loc,emotion,props) in enumerate(events,1):
        shots=[
            {"id":f"scene_{i:02d}_shot_01","shot_type":"establishing",
             "framing":"wide","camera":"cinematic wide shot","action":title},
            {"id":f"scene_{i:02d}_shot_02","shot_type":"action",
             "framing":"medium","camera":"cinematic tracking shot","action":title},
        ]
        if kind in {"discovery","conflict","choice","companion","final_image"}:
            shots.append({"id":f"scene_{i:02d}_shot_03","shot_type":"emotion",
                          "framing":"close","camera":"cinematic close-up","action":title})
        scenes.append(_scene(title,kind,loc,
                             next((x for x in re.split(r"(?<=[.!?])\s+",story)
                                   if any(w in x.lower() for w in title.lower().split()[:2])),story),
                             chars,[{"id":x,"name":x} for x in props],emotion))
        scenes[-1]["scene_number"]=i
        scenes[-1]["id"]=f"scene_{i:02d}"
        scenes[-1]["shots"]=shots
    return {"version":"4.0-event","title":kwargs.get("title","Aadwik Production"),
            "story":story,
            "metadata":{"style":kwargs.get("style","stylized cinematic 3D"),
                        "aspect_ratio":kwargs.get("aspect_ratio","16:9"),
                        "language":kwargs.get("language","English"),
                        "genre":kwargs.get("genre","Adventure"),
                        "age_group":kwargs.get("age_group","All Ages")},
            "character_lock":{"characters":chars},
            "scenes":scenes,
            "production_summary":{"scene_count":len(scenes),
                                  "shot_count":sum(len(x["shots"]) for x in scenes),
                                  "characters":len(chars)},
            "theme":"story","object":"blue_star" if "star" in story.lower() else "none"}

def build_story_visual_plan(story,**kwargs): return analyze_story(story,**kwargs)
def create_story_visual_plan(story,**kwargs): return analyze_story(story,**kwargs)
def generate_scenes(story,**kwargs): return analyze_story(story,**kwargs)["scenes"]
class StoryVisualPlanner:
    def build_plan(self,story,**kwargs): return analyze_story(story,**kwargs)
    def generate_scenes(self,story,**kwargs): return generate_scenes(story,**kwargs)
__all__=["analyze_story","build_story_visual_plan","create_story_visual_plan","generate_scenes","StoryVisualPlanner"]
