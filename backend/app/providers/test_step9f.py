import json
from pathlib import Path
from aadwik_world_continuity import lock_sequence
from aadwik_cinematic_continuity import validate_cinematic_continuity

# Step 9F uses explicit shot-level acting directives.
# No dependency on the existing 8F implementation is required.

shots=[
 {"shot_id":"01","world_id":"world_forest_moonlit_v1",
  "character_ids":["char_tara_v1"],"prop_ids":["prop_blue_star_v1"],
  "camera":{"position":[7,-9,5],"target":[0,0,2]},
  "acting":{"char_tara_v1":"look"}},
 {"shot_id":"02","world_id":"world_forest_moonlit_v1",
  "character_ids":["char_tara_v1","char_guardian_v1"],"prop_ids":["prop_blue_star_v1"],
  "camera":{"position":[5,-6,3.5],"target":[0,0,1.8]},
  "acting":{"char_tara_v1":"walk","char_guardian_v1":"injured"}},
 {"shot_id":"03","world_id":"world_forest_moonlit_v1",
  "character_ids":["char_tara_v1","char_guardian_v1","char_shadow_creature_v1"],"prop_ids":["prop_blue_star_v1"],
  "camera":{"position":[3,-5,2.8],"target":[0,0,1.5]},
  "acting":{"char_tara_v1":"look","char_guardian_v1":"injured","char_shadow_creature_v1":"threaten"}},
 {"shot_id":"04","world_id":"world_forest_moonlit_v1",
  "character_ids":["char_tara_v1","char_guardian_v1"],"prop_ids":["prop_blue_star_v1"],
  "camera":{"position":[-2,-7,3.2],"target":[0,0,1.7]},
  "acting":{"char_tara_v1":"reach","char_guardian_v1":"look"}},
]

locked=lock_sequence(shots)
report=validate_cinematic_continuity(locked)
assert report["valid"], report["issues"]

Path("step9f_cinematic_continuity_report.json").write_text(
    json.dumps(report,indent=2),encoding="utf-8"
)

print("ENVIRONMENT + CHARACTER + CAMERA: CONNECTED")
print("WORLD IDENTITY LOCK: OK")
print("CHARACTER IDENTITY LOCK: OK")
print("PROP IDENTITY LOCK: OK")
print("ACTING CONTINUITY: OK")
print("CAMERA SHOT-TO-SHOT CONTINUITY: OK")
print("CINEMATIC CONTINUITY: OK")
print("STEP 9F PASS")
