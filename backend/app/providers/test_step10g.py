from aadwik_full_audio_pipeline import validate_full_audio_package

p=validate_full_audio_package()
assert p["scenes"]==14
assert p["shots"]==41
assert p["tracks"]["voice"]==3
assert p["tracks"]["dialogue_lines"]>0
assert p["tracks"]["music_cues"]>0
assert p["tracks"]["sfx_cues"]>0
assert p["tracks"]["ambience_cues"]>0
assert p["synchronized"] is True
assert p["provider_agnostic"] is True

print("THE LAST STAR: FULL AUDIO PIPELINE")
print("14 SCENES: OK")
print("41 SHOTS: OK")
print("VOICE + DIALOGUE: OK")
print("MUSIC: OK")
print("SFX: OK")
print("AMBIENCE: OK")
print("AUDIO SYNCHRONIZATION: OK")
print("FULL AUDIO PACKAGE: OK")
print("STEP 10G PASS")
