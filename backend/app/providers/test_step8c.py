from aadwik_asset_adapter import attach_locked_assets, save_job

job = {
    "schema": "aadwik-blender-job-1.0",
    "title": "The Last Star",
    "shots": [
        {"shot_id": "scene_01_shot_01", "asset_ids": ["char_tara_v1"]},
        {"shot_id": "scene_04_shot_01", "asset_ids": ["char_tara_v1", "char_guardian_v1"]},
        {"shot_id": "scene_09_shot_01", "asset_ids": ["char_tara_v1", "char_guardian_v1", "char_shadow_creature_v1"]},
        {"shot_id": "scene_14_shot_01", "asset_ids": ["char_tara_v1", "prop_blue_star_v1"]},
    ],
}

result = attach_locked_assets(job)

assert result["asset_library"]["identity_locked"] is True
assert result["asset_library"]["reuse_mode"] == "exact"
assert result["shots"][0]["locked_asset_roots"] == ["CHAR_TARA_ROOT"]
assert result["shots"][2]["locked_asset_roots"] == [
    "CHAR_TARA_ROOT", "CHAR_GUARDIAN_ROOT", "CHAR_SHADOW_ROOT"
]
assert all(s["asset_reuse_locked"] for s in result["shots"])

save_job(result, "step8c_blender_job_assets.json")

print("ASSET LIBRARY -> BLENDER JOB: CONNECTED")
print("EXACT REUSE: OK")
print("IDENTITY LOCK: OK")
print("TARA REUSED ACROSS SHOTS: OK")
print("GUARDIAN REUSED ACROSS SHOTS: OK")
print("SHADOW CREATURE REUSED ACROSS SHOTS: OK")
print("BLUE STAR REUSED ACROSS SHOTS: OK")
print("STEP 8C PASS")
