from aadwik_full_sequence_test import run_step9g

report=run_step9g()
assert report["valid"], report["issues"]
assert report["scene_count"]==14
assert report["shot_count"]==41

print("THE LAST STAR: FULL 3D PRODUCTION SEQUENCE")
print("14 SCENES: OK")
print("41 SHOTS: OK")
print("LOCKED CHARACTERS: OK")
print("LOCKED PROPS: OK")
print("LOCKED WORLDS: OK")
print("SHOT IDENTITY / UNIQUENESS: OK")
print("FULL STORY SEQUENCE CONTRACT: OK")
print("STEP 9G PASS")
