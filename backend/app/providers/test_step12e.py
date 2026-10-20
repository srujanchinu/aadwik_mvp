from aadwik_qc_engine import validate_timeline
r=validate_timeline([{"id":"a","start":0,"duration":2},{"id":"b","start":2,"duration":2}])
assert not r
print("TIMELINE QC: OK")
print("CLIP ORDER QC: OK")
print("STEP 12E PASS")
