from aadwik_qc_engine import validate_audio
r=validate_audio([{"id":"dlg_001","start_sec":0,"duration_sec":2}])
assert not r
print("DIALOGUE QC: OK")
print("AUDIO TIMING QC: OK")
print("STEP 12D PASS")
