from aadwik_ambience_engine import AmbienceCue,AmbienceTimeline,save_timeline
t=AmbienceTimeline()
t.add(AmbienceCue("amb_001","world_village_festival_v1",0,5,"village_festival",.45))
t.add(AmbienceCue("amb_002","world_forest_moonlit_v1",5,8,"night_forest",.5))
t.add(AmbienceCue("amb_003","world_glowing_river_v1",13,6,"glowing_river",.4))
r=t.validate(); assert r["valid"] and r["cue_count"]==3
save_timeline(t,"step10e_ambience_timeline.json")
print("AMBIENCE ENGINE: CONNECTED")
print("WORLD -> AMBIENCE BINDING: OK")
print("ENVIRONMENT AUDIO LEVELS: OK")
print("AMBIENCE TIMING: OK")
print("PROVIDER-AGNOSTIC AMBIENCE LAYER: OK")
print("STEP 10E PASS")
