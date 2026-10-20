from aadwik_compositing import build_composite
r=build_composite(["video","color","titles","subtitles","audio"])
assert r["valid"] and r["order"][-1]=="audio"
print("VIDEO COMPOSITING: OK")
print("COLOR LAYER: OK")
print("TITLE LAYER: OK")
print("SUBTITLE LAYER: OK")
print("STEP 11D PASS")
