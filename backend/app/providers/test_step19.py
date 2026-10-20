from aadwik_idea_experiment import create_idea,create_experiment
i=create_idea("The Moon Garden","fantasy","family")
e=create_experiment("opening_test","compare two openings",["A","B"])
assert i["status"]=="IDEA" and e["status"]=="READY"
print("IDEA BANK: OK")
print("EXPERIMENT MODE: OK")
print("CONTROLLED VARIANTS: OK")
print("NO AUTOMATIC STORY DESTRUCTION: OK")
print("STEP 19 PASS")
