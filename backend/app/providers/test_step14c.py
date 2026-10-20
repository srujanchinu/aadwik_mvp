from aadwik_dialogue_localization import localize_dialogue
lines = [
 {"character":"tara","text":"We can help.","start":1.0,"duration":2.0,"emotion":"brave"},
 {"character":"guardian","text":"Thank you.","start":3.0,"duration":2.0,"emotion":"relieved"}
]
out = localize_dialogue(lines, "te")
assert all(x["timing_locked"] and x["emotion_locked"] for x in out)
assert all(x["language"] == "te" for x in out)
print("CHARACTER DIALOGUE LOCALIZATION: OK")
print("EMOTION LOCK: OK")
print("TIMING LOCK: OK")
print("STEP 14C PASS")
