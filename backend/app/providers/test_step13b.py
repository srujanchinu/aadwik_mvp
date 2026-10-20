from aadwik_production_orchestrator import create_job
from aadwik_movie_pipeline import run_movie_pipeline

payload = {
 "story":{"title":"The Last Star"},
 "shot_plan":{"scene_count":14,"shot_count":41},
 "assets":{"characters":["char_tara_v1","char_guardian_v1","char_shadow_creature_v1"],"props":["prop_blue_star_v1"]},
 "worlds":{"count":7},
 "acting":{"locked":True},
 "camera":{"shots":41},
 "audio":{"shot_count":41},
 "edit":{"clips":41},
 "qc":{"publishing_gate":True},
 "scenes":[{"scene":i} for i in range(14)]
}
job = create_job("the_last_star", "movie", payload["scenes"])
out = run_movie_pipeline(job, payload)
assert out["state"] == "READY_TO_PUBLISH"
assert out["scene_count"] == 14
print("STORY -> FULL MOVIE PIPELINE: CONNECTED")
print("14 SCENES: OK")
print("41 SHOTS: OK")
print("FULL PIPELINE STATE: READY_TO_PUBLISH")
print("STEP 13B PASS")
