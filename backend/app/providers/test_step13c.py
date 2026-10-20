from aadwik_series_pipeline import build_series_package

base = {
 "story":{"title":"Episode"},
 "shot_plan":{"shot_count":5},
 "assets":{"characters":["char_tara_v1"]},
 "worlds":{"count":1},
 "acting":{"locked":True},
 "camera":{"shots":5},
 "audio":{"shot_count":5},
 "edit":{"clips":5},
 "qc":{"publishing_gate":True},
 "scenes":[{"scene":1}]
}
series = {
 "series_id":"little_wonders_demo",
 "episodes":[
   {"episode_id":"ep01","production_payload":base},
   {"episode_id":"ep02","production_payload":base},
 ]
}
out = build_series_package(series)
assert out["episode_count"] == 2 and out["series_ready"]
print("SERIES -> EPISODE PIPELINE: CONNECTED")
print("2 EPISODES: OK")
print("EPISODE PRODUCTION REUSE: OK")
print("SERIES READY STATE: OK")
print("STEP 13C PASS")
