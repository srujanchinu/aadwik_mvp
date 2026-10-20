from aadwik_world_continuity import validate_sequence, lock_sequence, save_report

shots=[
 {"shot_id":"01","world_id":"world_forest_moonlit_v1","character_ids":["char_tara_v1"],"prop_ids":["prop_blue_star_v1"]},
 {"shot_id":"02","world_id":"world_forest_moonlit_v1","character_ids":["char_tara_v1","char_guardian_v1"],"prop_ids":["prop_blue_star_v1"]},
 {"shot_id":"03","world_id":"world_forest_moonlit_v1","character_ids":["char_tara_v1","char_guardian_v1","char_shadow_creature_v1"],"prop_ids":["prop_blue_star_v1"]},
 {"shot_id":"04","world_id":"world_forest_moonlit_v1","character_ids":["char_tara_v1","char_guardian_v1"],"prop_ids":["prop_blue_star_v1"]},
]

report=validate_sequence(shots)
assert report["valid"] is True
assert report["issues"]==[]

locked=lock_sequence(shots)
assert len(locked)==4
assert all(s["world_continuity_locked"] for s in locked)
assert all(s["world_instance_id"]=="world_forest_moonlit_v1" for s in locked)

save_report(report,"step9e_continuity_report.json")

print("4 CONSECUTIVE SHOTS VALIDATED")
print("SAME WORLD INSTANCE: OK")
print("LOCKED CHARACTER IDS: OK")
print("LOCKED PROP IDS: OK")
print("CHARACTER ENTRY/EXIT HANDLED: OK")
print("WORLD CONTINUITY: OK")
print("STEP 9E PASS")
