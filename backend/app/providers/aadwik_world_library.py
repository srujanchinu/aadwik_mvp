import json
from pathlib import Path

# STEP 9A — Reusable World/Environment Library.
# Lightweight schema first; actual Blender world builders plug into these locked IDs.

WORLD_LIBRARY={
 "world_village_festival_v1":{"world_id":"world_village_festival_v1","name":"Village Festival","type":"village","locked":True,
   "visual_lock":{"time":"night","mood":"warm magical festival","elements":["village homes","festival lights","open gathering area"]}},
 "world_forest_moonlit_v1":{"world_id":"world_forest_moonlit_v1","name":"Moonlit Forest","type":"forest","locked":True,
   "visual_lock":{"time":"night","mood":"mysterious magical","elements":["large trees","moonlight","glowing trail"]}},
 "world_ancient_tree_v1":{"world_id":"world_ancient_tree_v1","name":"Ancient Tree","type":"ancient_tree","locked":True,
   "visual_lock":{"time":"night","mood":"mystical","elements":["ancient tree","roots","soft magical light"]}},
 "world_glowing_river_v1":{"world_id":"world_glowing_river_v1","name":"Glowing River","type":"river","locked":True,
   "visual_lock":{"time":"night","mood":"wonder","elements":["glowing water","riverbank","reflections"]}},
 "world_ancient_temple_v1":{"world_id":"world_ancient_temple_v1","name":"Ancient Stone Temple","type":"temple","locked":True,
   "visual_lock":{"time":"night","mood":"mysterious","elements":["stone pillars","temple floor","shadowed chamber"]}},
 "world_village_home_v1":{"world_id":"world_village_home_v1","name":"Village Home","type":"home","locked":True,
   "visual_lock":{"time":"sunrise","mood":"peaceful","elements":["simple home","warm light","village surroundings"]}},
 "world_magical_forest_v1":{"world_id":"world_magical_forest_v1","name":"Awakened Magical Forest","type":"forest","locked":True,
   "visual_lock":{"time":"sunrise","mood":"hopeful transformation","elements":["trees","floating light","glowing plants"]}},
}

def get_world(world_id):
    world=WORLD_LIBRARY.get(world_id)
    if not world: raise ValueError(f"Unknown world: {world_id}")
    if not world["locked"]: raise ValueError(f"World not locked: {world_id}")
    return world

def resolve_worlds(world_ids):
    out=[]; seen=set()
    for wid in world_ids:
        if wid in seen: continue
        out.append(get_world(wid)); seen.add(wid)
    return out

def save_manifest(path):
    payload={"schema":"aadwik-world-library-1.0","world_count":len(WORLD_LIBRARY),
             "worlds":list(WORLD_LIBRARY.values())}
    Path(path).write_text(json.dumps(payload,indent=2),encoding="utf-8")
    return payload
