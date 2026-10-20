from pathlib import Path
import ast
R=Path(__file__).resolve().parents[1]; p=R/"app"/"renderer"/"local_video_provider.py"; s=R/"app"/"renderer"/"aadwik_animation_scene.py"
assert p.exists() and s.exists()
ast.parse(p.read_text()); ast.parse(s.read_text())
t=p.read_text()
assert all(x in t for x in ["sequence","frame_%04d.png","FFPROBE","PNG frames"])
assert "action.fcurves" not in s.read_text()
print("BATCH 34: 5/5 PASS")
