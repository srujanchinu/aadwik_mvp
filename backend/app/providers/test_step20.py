from aadwik_cost_provider import estimate_cost,choose_provider
assert estimate_cost("blender_local",100)==0
x=choose_provider("external_ai_video",10,100)
assert x["within_budget"] and x["provider"]=="blender_local"
print("PROVIDER ABSTRACTION: OK")
print("COST ESTIMATION: OK")
print("FREE-FIRST FALLBACK: OK")
print("COST PROTECTION: OK")
print("STEP 20 PASS")
