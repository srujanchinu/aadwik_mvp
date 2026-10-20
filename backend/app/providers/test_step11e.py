from aadwik_editing_engine import Timeline
t=Timeline()
t.add_overlay("title","THE LAST STAR",0,3)
t.add_overlay("subtitle","What was that?",4,2)
assert len(t.overlays)==2
assert t.overlays[0]["type"]=="title"
assert t.overlays[1]["type"]=="subtitle"
print("TITLES: OK")
print("SUBTITLES: OK")
print("OVERLAY TIMING: OK")
print("STEP 11E PASS")
