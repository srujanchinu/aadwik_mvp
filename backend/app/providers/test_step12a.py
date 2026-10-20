from aadwik_qc_engine import validate_visual
r=validate_visual([{"id":"shot_01","rendered":True,"width":640,"height":360}])
assert not r
print("VISUAL QUALITY GATE: OK")
print("RENDER VALIDITY: OK")
print("STEP 12A PASS")
