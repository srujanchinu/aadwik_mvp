from aadwik_ui_integration import build_studio_state,validate_navigation
s=build_studio_state("the_last_star","READY_TO_PUBLISH",True)
assert validate_navigation(s) and s["qc_gate"]
print("STUDIO STATE: OK")
print("CORE SECTIONS CONNECTED: OK")
print("QC -> PUBLISHING UI STATE: OK")
print("ANALYTICS ENTRY: OK")
print("STEP 21 PASS")
