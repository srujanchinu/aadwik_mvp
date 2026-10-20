from aadwik_shot_acting_director import direct_job, save_job

job={
 "title":"The Last Star",
 "shots":[
  {"shot_id":"s01","event_type":"discovery","characters":["char_tara_v1"],"emotion":"wonder","start_frame":1,"end_frame":32},
  {"shot_id":"s02","event_type":"journey","characters":["char_tara_v1","char_guardian_v1"],"emotion":"cautious","start_frame":1,"end_frame":32},
  {"shot_id":"s03","event_type":"conflict","characters":["char_tara_v1","char_guardian_v1","char_shadow_creature_v1"],"emotion":"fear","start_frame":1,"end_frame":32},
  {"shot_id":"s04","event_type":"resolution","characters":["char_tara_v1","char_guardian_v1"],"emotion":"hope","start_frame":1,"end_frame":32},
 ]
}
out=direct_job(job)
acts=[[d["character_id"],d["action"]] for s in out["shots"] for d in s["acting_directives"]]
print("ACTING DIRECTIVES:",acts)
assert ["char_tara_v1","look"] in acts
assert ["char_tara_v1","walk"] in acts
assert ["char_guardian_v1","injured"] in acts
assert ["char_shadow_creature_v1","threaten"] in acts
assert out["acting_system"]["story_driven"] is True
assert all(s["acting_director_locked"] for s in out["shots"])
save_job(out,"step8f_acting_job.json")
print("SHOT -> ACTING: CONNECTED")
print("STORY-DRIVEN ACTIONS: OK")
print("IDENTITY LOCK: OK")
print("STEP 8F PASS")
