from aadwik_subtitle_engine import build_subtitles
lines = [
 {"character":"tara","text":"Hello","start":0.0,"duration":2.0},
 {"character":"guardian","text":"Welcome","start":2.0,"duration":2.0}
]
out = build_subtitles(lines, "te")
assert len(out["subtitles"]) == 2
assert out["timing_locked"]
assert out["subtitles"][1]["start"] == 2.0
print("SUBTITLE GENERATION: OK")
print("SUBTITLE TIMING: OK")
print("STEP 14E PASS")
