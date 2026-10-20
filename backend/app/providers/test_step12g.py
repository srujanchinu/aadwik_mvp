from aadwik_qc_engine import run_full_qc
r=run_full_qc()
assert r["valid"]
assert r["publishing_gate"] if "publishing_gate" in r else r["gates"]["publishing_gate"]
assert all(r["gates"].values())
print("THE LAST STAR: FULL MOVIE QC")
print("VISUAL QUALITY: PASS")
print("CHARACTER / PROP IDENTITY: PASS")
print("WORLD CONTINUITY: PASS")
print("AUDIO: PASS")
print("TIMELINE: PASS")
print("STORY COMPLETENESS: PASS")
print("PUBLISHING QC GATE: OPEN")
print("STEP 12G PASS")
