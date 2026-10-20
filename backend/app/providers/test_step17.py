from aadwik_brain_memory import build_context,recall
c=build_context("the_last_star",{"world":"locked"},{"tara":{"age":12}})
assert c["continuity_lock"] and recall(c,"character_memory")["tara"]["age"]==12
print("AADWIK BRAIN CONTEXT: OK")
print("STORY BIBLE MEMORY: OK")
print("CHARACTER MEMORY: OK")
print("CONTINUITY LOCK: OK")
print("STEP 17 PASS")
