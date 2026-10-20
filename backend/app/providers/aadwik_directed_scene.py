import bpy
from mathutils import Vector
from pathlib import Path
import runpy

# STEP 9D — Apply shot-level acting directives to characters inside a real world.

ACTION_OFFSETS={
 "idle":(0,0,0),
 "look":(0,0,.05),
 "walk":(.7,0,0),
 "reach":(0,-.15,.08),
 "injured":(-.12,0,0),
 "threaten":(0,.12,.10),
}

def apply_action(root, action):
    if action not in ACTION_OFFSETS:
        action="idle"
    root.location += Vector(ACTION_OFFSETS[action])
    return action

def assemble_directed_scene(world_id, asset_ids, directives, output):
    world=runpy.run_path("aadwik_world_builder.py")
    assets=runpy.run_path("aadwik_asset_injector.py")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    world_col=world["build_world"](world_id)
    library=assets["build_library"]()
    injected=assets["inject"](asset_ids,library)

    roots={}
    positions={
        "char_tara_v1":(-1.2,-1.0,0),
        "char_guardian_v1":(0,-.6,0),
        "char_shadow_creature_v1":(2,1,0),
        "prop_blue_star_v1":(.5,-1,2.8),
    }
    for aid,col in injected:
        for obj in col.objects:
            if obj.parent is None:
                obj.location += Vector(positions.get(aid,(0,0,0)))
                roots[aid]=obj

    applied=[]
    for d in directives:
        aid=d["asset_id"]
        if aid in roots:
            applied.append((aid,apply_action(roots[aid],d.get("action","idle"))))

    bpy.ops.object.camera_add(location=(0,-13,5))
    cam=bpy.context.object
    cam.name="CAM_DIRECTED_SCENE"
    cam.data.lens=50
    cam.rotation_euler=(Vector((0,0,1.5))-cam.location).to_track_quat("-Z","Y").to_euler()
    bpy.context.scene.camera=cam

    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE"
    scene.render.resolution_x=480; scene.render.resolution_y=270; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(Path(output).resolve())
    bpy.ops.render.render(write_still=True)
    assert Path(output).exists()
    return world_col,applied

print("AADWIK_STEP9D_DIRECTED_SCENE_READY")
