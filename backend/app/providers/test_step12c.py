from aadwik_qc_engine import validate_identity
r=validate_identity([{"world_id":"world_forest_moonlit_v1","character_ids":["char_tara_v1"],"prop_ids":[]}],
{"char_tara_v1"},{"prop_blue_star_v1"},{"world_forest_moonlit_v1"})
assert not r
print("WORLD CONTINUITY QC: OK")
print("CHARACTER CONTINUITY QC: OK")
print("STEP 12C PASS")
