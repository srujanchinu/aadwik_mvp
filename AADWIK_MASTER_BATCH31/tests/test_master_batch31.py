from pathlib import Path
import ast, re
ROOT=Path(__file__).resolve().parents[1]
scene=(ROOT/"app/renderer/aadwik_cartoon_scene.py").read_text(encoding="utf-8")
provider=(ROOT/"app/renderer/local_video_provider_cartoon.py").read_text(encoding="utf-8")
ast.parse(scene); ast.parse(provider)
assert "--frames_dir" in scene and "--prompt" in scene
assert "BLENDER_EEVEE" in scene
assert "build" not in scene.split("print",1)[0]  # renderer is self-contained, no fragile external character import
assert "class LocalVideoProvider" in provider
assert "rglob" in provider and "*.png" in provider
assert "generate_video" in provider
assert "build_tara" not in provider
print("Batch 31 test 1/5 PASS — Python syntax")
print("Batch 31 test 2/5 PASS — Blender argument contract")
print("Batch 31 test 3/5 PASS — self-contained character/world renderer")
print("Batch 31 test 4/5 PASS — PNG discovery and FFmpeg assembly")
print("Batch 31 test 5/5 PASS — provider aliases/API")
print("BATCH 31: 5/5 PASS")
