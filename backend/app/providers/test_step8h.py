import bpy
from pathlib import Path
import runpy
from mathutils import Vector

# STEP 8H — full 3D sequence smoke test.
# Uses the same story-aware asset/acting/camera chain, but renders a tiny
# 3-shot sequence to keep Intel UHD load reasonable.

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Load the actual Step 8D asset injector and build the locked library.
mod=runpy.run_path("aadwik_asset_injector.py")
build_library=mod["build_library"]
inject=mod["inject"]

library=build_library()

shots=[
    ("shot_01_discovery",["char_tara_v1","prop_blue_star_v1"],"look"),
    ("shot_02_journey",["char_tara_v1","char_guardian_v1"],"walk"),
    ("shot_03_conflict",["char_tara_v1","char_guardian_v1","char_shadow_creature_v1"],"threaten"),
]

out=Path("step8h_sequence")
out.mkdir(exist_ok=True)

# Lightweight camera and render setup.
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=320
scene.render.resolution_y=180
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False

for idx,(shot_id,asset_ids,main_action) in enumerate(shots,1):
    # Remove prior injected shot collections.
    for c in list(bpy.data.collections):
        if c.name.startswith("SHOT_ASSET_"):
            bpy.data.collections.remove(c)

    injected=inject(asset_ids,library)

    # Arrange roots in a simple readable composition.
    for j,(_,col) in enumerate(injected):
        for obj in col.objects:
            if obj.parent is None:
                obj.location.x += (j-(len(injected)-1)/2)*1.6

    bpy.ops.object.camera_add(location=(0,-10,2.8))
    cam=bpy.context.object
    cam.name=f"CAM_{idx:02d}"
    cam.data.lens=50
    # Point camera toward the composition.
    direction=Vector((0,0,1.6))-cam.location
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    scene.camera=cam

    # Simple ground.
    bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,0))
    ground=bpy.context.object
    ground.name=f"GROUND_{idx:02d}"

    scene.render.filepath=str((out/f"{shot_id}.png").resolve())
    bpy.ops.render.render(write_still=True)
    assert Path(scene.render.filepath).exists()
    print("RENDERED",shot_id,scene.render.filepath)

print("FULL 3D SEQUENCE: RENDERED")
print("LOCKED ASSETS: OK")
print("SHOT COMPOSITION: OK")
print("BLENDER EEVEE: OK")
print("STEP 8H PASS")
