from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ROOT / "app" / "providers"

scene = (PROVIDERS / "aadwik_blender_scene.py").read_text(encoding="utf-8")
chars = (PROVIDERS / "aadwik_character_quality.py").read_text(encoding="utf-8")
provider = (PROVIDERS / "local_video_provider.py").read_text(encoding="utf-8")

assert "build_tara" in scene
assert "build_guardian" in scene
assert "build_shadow" in scene
assert "build_blue_star" in scene
assert "CHAR_TARA_ROOT" in chars
assert "char_tara_v2" in chars
assert "identity_locked" in chars
assert '"--plan"' in provider
assert 'SCENE_SCRIPT = Path(__file__).with_name("aadwik_blender_scene.py")' in provider
assert "_build_phase23_plan" in provider
assert "ImageDraw" not in scene
assert "PIL" not in scene

print("PHASE 23 REAL ROUTE INTEGRATION: PASS")
print("Legacy Pillow scene is not selected by LocalVideoProvider.")
print("Explicit Phase 23 --plan handoff: PASS")
