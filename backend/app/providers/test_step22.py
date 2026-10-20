from aadwik_end_to_end import run_e2e
r=run_e2e()
assert r["all_connected"] and r["status"]=="READY" and len(r["stages"])==12
print("AADWIK END-TO-END SYSTEM")
print("IDEA -> STORY: PASS")
print("STORY -> 3D: PASS")
print("3D -> AUDIO -> EDITING: PASS")
print("QC -> LOCALIZATION: PASS")
print("PUBLISHING -> SOCIAL -> ANALYTICS: PASS")
print("ALL CORE STAGES CONNECTED: PASS")
print("STEP 22 PASS")
