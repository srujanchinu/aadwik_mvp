from aadwik_character_camera_integrator import integrate_job,save_job

job={"title":"The Last Star","shots":[
 {"shot_id":"scene_02_shot_01","event_type":"discovery","characters":["char_tara_v1"],"emotion":"wonder","camera_id":"CAM_02_01","framing":"wide","lens_mm":35,"camera_movement":"push_in"},
 {"shot_id":"scene_09_shot_01","event_type":"conflict","characters":["char_tara_v1","char_guardian_v1","char_shadow_creature_v1"],"emotion":"fear","camera_id":"CAM_09_01","framing":"medium_wide","lens_mm":50,"camera_movement":"slow_dolly"},
 {"shot_id":"scene_11_shot_01","event_type":"resolution","characters":["char_tara_v1","char_guardian_v1","prop_blue_star_v1"],"emotion":"hope","camera_id":"CAM_11_01","framing":"close","lens_mm":70,"camera_movement":"orbit"},
]}

out=integrate_job(job)
s2=out["shots"][1]
bindings={x["character_id"]:x for x in s2["asset_bindings"]}
assert bindings["char_tara_v1"]["action"]=="look"
assert bindings["char_guardian_v1"]["action"]=="injured"
assert bindings["char_shadow_creature_v1"]["action"]=="threaten"
assert s2["camera_binding"]["camera_locked"] is True
assert all(s["production_ready"] for s in out["shots"])
assert out["integration"]["asset_identity_locked"]
save_job(out,"step8g_integrated_job.json")
print("ASSET + ACTING + CAMERA: CONNECTED")
print("TARA CONFLICT ACTION: LOOK (SAFE)")
print("GUARDIAN CONFLICT ACTION: INJURED")
print("SHADOW CONFLICT ACTION: THREATEN")
print("CAMERA BINDING: OK")
print("PRODUCTION READY SHOTS: OK")
print("STEP 8G PASS")
