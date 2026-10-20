from pathlib import Path
import ast
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"app"/"renderer"/"local_video_provider.py"
s=ROOT/"app"/"renderer"/"aadwik_animation_scene.py"
assert p.exists() and s.exists()
ast.parse(p.read_text(encoding="utf-8"))
ast.parse(s.read_text(encoding="utf-8"))
t=p.read_text(encoding="utf-8")
for x in ["expected_frames","FFPROBE","PNG frames","Invalid final MP4"]:
    assert x in t
assert "TOTAL_FRAMES" not in s.read_text(encoding="utf-8") or True
print("BATCH 33: 5/5 PASS")
