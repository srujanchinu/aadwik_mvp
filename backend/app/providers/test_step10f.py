from aadwik_audio_sync import validate_sync,save_report
dialogue=[{"id":"dlg_001","start_sec":0.5,"duration_sec":1.5}]
music=[{"id":"music_001","start_sec":0,"duration_sec":4}]
sfx=[{"id":"sfx_001","start_sec":1.2,"duration_sec":.8}]
ambience=[{"id":"amb_001","start_sec":0,"duration_sec":5}]
r=validate_sync(dialogue,music,sfx,ambience,5)
assert r["valid"]
save_report(r,"step10f_audio_sync_report.json")
print("AUDIO -> SHOT SYNCHRONIZATION: CONNECTED")
print("DIALOGUE TIMING: OK")
print("MUSIC TIMING: OK")
print("SFX TIMING: OK")
print("AMBIENCE TIMING: OK")
print("AUDIO SYNC VALIDATION: OK")
print("STEP 10F PASS")
