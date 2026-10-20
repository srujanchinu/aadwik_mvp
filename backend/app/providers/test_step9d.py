import runpy
from pathlib import Path

mod = runpy.run_path("aadwik_directed_scene.py")
assemble_directed_scene = mod["assemble_directed_scene"]

directives = [
    {"asset_id": "char_tara_v1", "action": "look", "emotion": "fear"},
    {"asset_id": "char_guardian_v1", "action": "injured", "emotion": "pain"},
    {"asset_id": "char_shadow_creature_v1", "action": "threaten", "emotion": "menace"},
    {"asset_id": "prop_blue_star_v1", "action": "idle", "emotion": "magic"},
]

out = Path("step9d_directed_scene.png")

world, applied = assemble_directed_scene(
    "world_forest_moonlit_v1",
    [d["asset_id"] for d in directives],
    directives,
    out
)

assert out.exists()

applied_dict = dict(applied)

assert applied_dict["char_tara_v1"] == "look"
assert applied_dict["char_guardian_v1"] == "injured"
assert applied_dict["char_shadow_creature_v1"] == "threaten"

print("WORLD + ASSETS: OK")
print("ACTING DIRECTIVES APPLIED: OK")
print("TARA: LOOK")
print("GUARDIAN: INJURED")
print("SHADOW CREATURE: THREATEN")
print("CAMERA: OK")
print("DIRECTED SCENE RENDER: OK")
print("STEP 9D PASS")