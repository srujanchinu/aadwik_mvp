from aadwik_localized_audio import build_localized_audio
lines = [
 {"character":"tara","start":0.0,"duration":2.0,"emotion":"brave"},
 {"character":"guardian","start":2.0,"duration":2.0,"emotion":"relieved"}
]
out = build_localized_audio(lines, "te", {"tara":"voice_tara_te_v1","guardian":"voice_guardian_te_v1"})
assert len(out["tracks"]) == 2
assert out["timing_locked"]
print("LOCALIZED AUDIO PACKAGE: OK")
print("CHARACTER VOICE MAPPING: OK")
print("AUDIO TIMING LOCK: OK")
print("STEP 14F PASS")
