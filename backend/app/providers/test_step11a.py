from aadwik_editing_engine import Timeline,Clip,save
t=Timeline()
for i in range(4): t.add_clip(Clip(f"clip_{i+1:03d}",f"shot_{i+1:02d}",i*4,4,f"shot_{i+1:02d}.mp4"))
r=t.validate(); assert r["valid"] and r["clip_count"]==4
save(t,"step11a_timeline.json")
print("SHOT -> CLIP ASSEMBLY: OK")
print("CLIP ORDERING: OK")
print("TIMELINE ENGINE: CONNECTED")
print("STEP 11A PASS")
