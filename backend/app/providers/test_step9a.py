from pathlib import Path
from aadwik_world_library import WORLD_LIBRARY, resolve_worlds, save_manifest

assert len(WORLD_LIBRARY)==7
resolved=resolve_worlds([
 "world_village_festival_v1",
 "world_forest_moonlit_v1",
 "world_ancient_tree_v1",
 "world_glowing_river_v1",
 "world_ancient_temple_v1",
 "world_village_home_v1",
 "world_magical_forest_v1",
 "world_forest_moonlit_v1",
])
assert len(resolved)==7
assert all(w["locked"] for w in resolved)
save_manifest("step9a_world_manifest.json")
assert Path("step9a_world_manifest.json").exists()

print("WORLD LIBRARY VERSION: 1.0")
print("TOTAL LOCKED WORLDS:",len(WORLD_LIBRARY))
print("WORLD RESOLUTION:",[w["world_id"] for w in resolved])
print("DUPLICATE REUSE: OK")
print("WORLD IDENTITY LOCK: OK")
print("STEP 9A PASS")
