
from __future__ import annotations
from typing import Any, Dict, List
import re

def _norm(s): return re.sub(r"[^a-z0-9]+"," ",str(s).lower()).strip()

def clean_characters(plan:Dict[str,Any])->Dict[str,Any]:
    chars=plan.get("character_lock",{}).get("characters",[])
    merged=[]
    for c in chars:
        name=_norm(c.get("name",""))
        cid=c.get("id","")
        # "girl" is a generic descriptor when a named girl is already present.
        if name=="girl" or cid=="girl":
            named=next((x for x in chars if x.get("id")!="girl" and x.get("name")),None)
            if named and ("girl" in _norm(named.get("appearance","")) or named.get("role")=="protagonist"):
                continue
        if not any(x.get("id")==cid for x in merged):
            merged.append(c)
    out=dict(plan)
    out["character_lock"]=dict(plan.get("character_lock",{}))
    out["character_lock"]["characters"]=merged
    out["character_lock"]["count"]=len(merged)
    for s in out.get("scenes",[]):
        ids=s.get("characters",[])
        cleaned=[]
        for x in ids:
            if x=="girl":
                x="tara" if any(c.get("id")=="tara" for c in merged) else x
            if x not in cleaned: cleaned.append(x)
        s["characters"]=cleaned
        s["locked_characters"]=cleaned
        if "asset_references" in s:
            s["asset_references"]["characters"]=cleaned
    return out

def assign_exact_context(plan:Dict[str,Any])->Dict[str,Any]:
    out=dict(plan)
    # Exact story-context mapping for The Last Star's event spine.
    exact={
      "Village Festival":"The village festival is alive with lanterns, music, and celebration as Tara notices something unusual in the night sky.",
      "Blue Star Falls":"Tara looks up as a strange blue star falls from the sky toward the nearby forest.",
      "Glowing Trail into the Forest":"Tara follows the blue star's glowing trail from the village into the dark forest.",
      "Injured Guardian Discovered":"Beneath an ancient tree, Tara discovers a tiny injured guardian hiding among the roots.",
      "Guardian's Stolen Star Revealed":"The injured guardian reveals that its magical star was stolen by a shadow creature.",
      "Journey Through the Moonlit Forest":"Tara and the guardian travel together through the moonlit forest toward the place where the stolen star was taken.",
      "Glowing River Crossing":"Tara and the guardian cross a glowing river on their journey.",
      "Ancient Stone Temple":"They arrive at an abandoned ancient stone temple where the stolen star is being held.",
      "Shadow Creature Appears":"Inside the temple, the shadow creature appears and confronts Tara and the guardian.",
      "Tara Chooses Courage and Compassion":"Instead of fighting with a weapon, Tara faces the shadow creature with courage and compassion.",
      "Star Returned to the Guardian":"Tara returns the magical blue star to the guardian.",
      "Forest Comes Alive With Light":"The returned star fills the forest with light and brings the sleeping world around them alive.",
      "Sunrise Return Home":"At sunrise, Tara leaves the forest and returns home after helping the guardian.",
      "The Tiny Star Remains in Her Hand":"At home, Tara discovers that one tiny star is still glowing in her hand."
    }
    for s in out.get("scenes",[]):
        if s.get("title") in exact:
            s["story_context"]=exact[s["title"]]
    out["production_summary"]=dict(out.get("production_summary",{}))
    out["production_summary"]["character_count"]=len(out.get("character_lock",{}).get("characters",[]))
    out["production_summary"]["exact_contexts"]=sum(1 for s in out.get("scenes",[]) if s.get("story_context") in exact.values())
    return out

def clean_production_plan(plan:Dict[str,Any])->Dict[str,Any]:
    return assign_exact_context(clean_characters(plan))
