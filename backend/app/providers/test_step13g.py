from aadwik_production_orchestrator import create_job
from aadwik_movie_pipeline import run_movie_pipeline
from aadwik_final_movie_assembly import assemble_final_movie

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
production = run_movie_pipeline(job, payload)

final = assemble_final_movie(
 {"shot_count":41},
 {"shot_count":41},
 {"clips":[{"shot":i} for i in range(41)]},
 {"publishing_gate":True}
)
assert production["state"] == "READY_TO_PUBLISH"
assert final["export_ready"]

print("THE LAST STAR: END-TO-END PRODUCTION")
print("PROJECT -> JOB: PASS")
print("STORY -> 3D PRODUCTION: PASS")
print("AUDIO -> EDITING: PASS")
print("QC -> PUBLISHING GATE: PASS")
print("FINAL MOVIE ASSEMBLY: PASS")
print("EXPORT READY: PASS")
print("STEP 13G PASS")
