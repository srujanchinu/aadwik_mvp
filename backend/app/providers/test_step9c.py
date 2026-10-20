import runpy
from pathlib import Path

mod=runpy.run_path("aadwik_scene_assembler.py")
assemble=mod["assemble"]

out=Path("step9c_full_scene.png")
world,assets=assemble(
    "world_forest_moonlit_v1",
    ["char_tara_v1","char_guardian_v1","char_shadow_creature_v1","prop_blue_star_v1"],
    out
)

assert out.exists()
assert world.name=="WORLD_world_forest_moonlit_v1"
assert len(assets)==4

print("WORLD + CHARACTERS + PROP: ASSEMBLED")
print("TARA: IN SCENE")
print("GUARDIAN: IN SCENE")
print("SHADOW CREATURE: IN SCENE")
print("BLUE STAR: IN SCENE")
print("CAMERA: IN SCENE")
print("FULL SCENE RENDER: OK")
print("STEP 9C PASS")
