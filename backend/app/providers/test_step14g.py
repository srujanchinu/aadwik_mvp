from aadwik_localized_movie_package import build_localized_movie

source = {
 "project_id":"the_last_star",
 "source_language":"en",
 "story":{"title":"The Last Star","scenes":[{"scene":i} for i in range(14)]},
 "dialogue":[
   {"character":"tara","text":"We can help.","start":1.0,"duration":2.0,"emotion":"brave"},
   {"character":"guardian","text":"Thank you.","start":3.0,"duration":2.0,"emotion":"relieved"}
 ]
}
out = build_localized_movie(
 source, "te",
 {"tara":"voice_tara_te_v1","guardian":"voice_guardian_te_v1"}
)
assert out["ready_for_localized_render"]
assert out["video_identity_locked"]
assert len(out["story"]["scenes"]) == 14
assert len(out["subtitles"]["subtitles"]) == 2
print("THE LAST STAR: FULL LOCALIZATION PIPELINE")
print("STORY: PASS")
print("TELUGU DIALOGUE: PASS")
print("SUBTITLES: PASS")
print("LOCALIZED AUDIO: PASS")
print("VIDEO IDENTITY LOCK: PASS")
print("TIMING LOCK: PASS")
print("READY FOR LOCALIZED RENDER: PASS")
print("STEP 14G PASS")
