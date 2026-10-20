from aadwik_editing_engine import Timeline,Clip
t=Timeline()
for i in range(3): t.add_clip(Clip(str(i),str(i),i*5,5,"x"))
t.add_transition("0","1","cut"); t.add_transition("1","2","dissolve")
r=t.validate(); assert r["valid"] and r["transition_count"]==2
print("TIMELINE SEQUENCING: OK")
print("TRANSITIONS: OK")
print("STEP 11B PASS")
