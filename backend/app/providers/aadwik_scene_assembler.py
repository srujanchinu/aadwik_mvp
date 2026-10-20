import bpy
from mathutils import Vector
from pathlib import Path

# STEP 9C — Full Scene Assembly smoke test.
# Assembles one real world, locked characters/prop, acting, and camera.

def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name.startswith(("WORLD_","SHOT_ASSET_")):
            try: bpy.data.collections.remove(c)
            except: pass

def load_module(path):
    import runpy
    return runpy.run_path(path)

def assemble(world_id, asset_ids, output):
    clear()
    world=load_module("aadwik_world_builder.py")
    assets=load_module("aadwik_asset_injector.py")
    col=world["build_world"](world_id)
    library=assets["build_library"]()
    injected=assets["inject"](asset_ids,library)

    # Position injected characters/props inside the environment.
    positions={
        "char_tara_v1":(-1.2,-1.0,0),
        "char_guardian_v1":(0.0,-.6,0),
        "char_shadow_creature_v1":(2.0,1.0,0),
        "prop_blue_star_v1":(0.5,-1.0,2.8),
    }
    for aid,c in injected:
        for obj in c.objects:
            if obj.parent is None and aid in positions:
                obj.location += Vector(positions[aid])

    # Camera looks toward the assembled story area.
    bpy.ops.object.camera_add(location=(0,-13,5.0))
    cam=bpy.context.object
    cam.name="CAM_FULL_SCENE"
    cam.data.lens=48
    cam.rotation_euler=(Vector((0,0,1.5))-cam.location).to_track_quat("-Z","Y").to_euler()
    bpy.context.scene.camera=cam

    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE"
    scene.render.resolution_x=480
    scene.render.resolution_y=270
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(Path(output).resolve())
    bpy.ops.render.render(write_still=True)

    assert Path(output).exists()
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(output).with_suffix(".blend").resolve()))
    return col,injected

print("AADWIK_STEP9C_SCENE_ASSEMBLY_READY")
