
import sys
from pathlib import Path

PROVIDER_DIR = Path(__file__).resolve().parent
if str(PROVIDER_DIR) not in sys.path:
    sys.path.insert(0, str(PROVIDER_DIR))

import bpy
import json
import math
import argparse
from mathutils import Vector

from aadwik_character_quality import (
    build_tara,
    build_guardian,
    build_shadow,
    build_blue_star,
    apply_emotion,
)

def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

def normalize_location(location):
    if isinstance(location, dict):
        value = location.get("kind", "fantasy")
    elif isinstance(location, str):
        value = location
    else:
        value = "fantasy"
    value = str(value or "fantasy").lower().strip()
    aliases = {
        "moonlit_forest":"forest",
        "enchanted_forest":"forest",
        "magical_forest":"forest",
        "forest_moonlit":"forest",
        "riverbank":"river",
    }
    return aliases.get(value, value)

def mat(name, color, rough=0.7, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (*color,1)
        b.inputs["Roughness"].default_value = rough
        if emission is not None:
            if "Emission Color" in b.inputs:
                b.inputs["Emission Color"].default_value = (*emission,1)
            if "Emission Strength" in b.inputs:
                b.inputs["Emission Strength"].default_value = 2.0
    return m

def add_ground(kind):
    m = mat("MAT_ENV_Ground", (0.028,0.07,0.04), 0.92)
    bpy.ops.mesh.primitive_plane_add(size=35, location=(0,0,0))
    ground = bpy.context.object
    ground.name = "ENV_GROUND"
    ground.data.materials.append(m)

    if kind == "forest":
        tree_m = mat("MAT_ENV_Trunk", (0.055,0.028,0.018), 0.95)
        leaf_m = mat("MAT_ENV_Leaf", (0.018,0.075,0.035), 0.9)
        for i,(x,y,s) in enumerate([
            (-7,4,1.5),(-5,-2,1.1),(5,3,1.5),(7,-1,1.2),
            (-8,-5,1.2),(8,5,1.4),(-3,6,1.0),(3,6,1.1)
        ]):
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.25*s, depth=3.2*s, location=(x,y,1.6*s))
            trunk=bpy.context.object; trunk.name=f"TREE_TRUNK_{i}"; trunk.data.materials.append(tree_m)
            for z in (2.7*s,3.5*s):
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0*s, location=(x,y,z))
                leaf=bpy.context.object; leaf.name=f"TREE_CANOPY_{i}_{z}"; leaf.scale=(1.15,1.0,.9); leaf.data.materials.append(leaf_m)
                for p in leaf.data.polygons: p.use_smooth=True

def setup_world(kind):
    w=bpy.context.scene.world
    if w is None:
        w=bpy.data.worlds.new("Aadwik World"); bpy.context.scene.world=w
    w.use_nodes=True
    b=w.node_tree.nodes.get("Background")
    if b:
        b.inputs["Color"].default_value=(0.006,0.012,0.035,1)
        b.inputs["Strength"].default_value=0.20

def add_lighting():
    # Moon key
    bpy.ops.object.light_add(type="AREA", location=(-3,-4,7))
    key=bpy.context.object; key.name="LIGHT_MOON"; key.data.energy=1100; key.data.size=7
    key.data.color=(0.55,0.68,1.0)
    key.rotation_euler=(math.radians(28),0,math.radians(-20))

    # Warm face fill
    bpy.ops.object.light_add(type="AREA", location=(3,-5,3))
    fill=bpy.context.object; fill.name="LIGHT_FACE_FILL"; fill.data.energy=650; fill.data.size=4
    fill.data.color=(1.0,0.62,0.40)
    fill.rotation_euler=(math.radians(72),0,math.radians(150))

    # Blue practical
    bpy.ops.object.light_add(type="POINT", location=(0,-0.5,2.5))
    p=bpy.context.object; p.name="LIGHT_STAR_GLOW"; p.data.energy=850; p.data.color=(0.10,0.35,1.0)

    # Rim
    bpy.ops.object.light_add(type="AREA", location=(3,3,4))
    rim=bpy.context.object; rim.name="LIGHT_RIM"; rim.data.energy=850; rim.data.size=4
    rim.data.color=(0.25,0.55,1.0)
    rim.rotation_euler=(math.radians(65),0,math.radians(-145))

def look_at(camera, target):
    direction=Vector(target)-camera.location
    if direction.length:
        camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()

def add_camera(shot_type, scene_index):
    if shot_type=="close":
        loc=(0,-7.0,2.65); lens=62
    elif shot_type=="wide":
        loc=(0,-12.5,4.8); lens=48
    else:
        loc=(0,-9.0,3.1); lens=55
    bpy.ops.object.camera_add(location=loc)
    cam=bpy.context.object
    cam.name=f"CAMERA_{scene_index:02d}"
    cam.data.lens=lens
    cam.data.sensor_width=36
    look_at(cam,(0,0,1.45))
    return cam

def choose_shot(scene_data):
    text=" ".join(str(scene_data.get(k,"")) for k in ("title","description","story_context")).lower()
    if any(x in text for x in ("discover","glow","wonder","emotion","close","face","star")):
        return "close"
    if any(x in text for x in ("forest","journey","wide","arrive","landscape")):
        return "wide"
    return "medium"

def scene_characters(scene_data):
    chars=scene_data.get("characters",[])
    if not isinstance(chars,list): chars=[]
    names={str(x).lower() for x in chars}
    tara=build_tara()
    tara.location=(-0.75,0,0)
    guardian=None
    shadow=None
    if any("guardian" in n for n in names):
        guardian=build_guardian()
        guardian.location=(0.85,0.15,0.0)
        guardian.scale=(0.72,0.72,0.72)
    if any("shadow" in n for n in names):
        shadow=build_shadow()
        shadow.location=(2.8,1.2,0)
        shadow.scale=(0.75,0.75,0.75)
    return tara,guardian,shadow

def add_star(scene_data):
    text=" ".join(str(scene_data.get(k,"")) for k in ("title","description","story_context","props")).lower()
    if "star" not in text:
        return None
    star=build_blue_star()
    star.location=(0.65,-0.25,2.45)
    star.scale=(0.9,0.9,0.9)
    return star

def parse_args():
    raw=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:]
    p=argparse.ArgumentParser()
    p.add_argument("--plan",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--width",type=int,default=640)
    p.add_argument("--height",type=int,default=360)
    p.add_argument("--fps",type=int,default=8)
    return p.parse_args(raw)

def main():
    args=parse_args()
    plan_path=Path(args.plan).resolve()
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)

    plan=json.loads(plan_path.read_text(encoding="utf-8"))
    scenes=plan.get("scenes",[])
    if not isinstance(scenes,list) or not scenes:
        raise RuntimeError("Phase 23 production plan contains no scenes.")

    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE"
    scene.render.resolution_x=args.width
    scene.render.resolution_y=args.height
    scene.render.resolution_percentage=100
    scene.render.fps=args.fps
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGBA"
    scene.render.film_transparent=False

    frame=1
    for idx, data in enumerate(scenes,1):
        clear()
        kind=normalize_location(data.get("location","forest"))
        print(f"[AADWIK VISUAL] SCENE {idx} LOCATION: {kind}",flush=True)

        setup_world(kind)
        add_ground(kind)
        add_lighting()

        tara,guardian,shadow=scene_characters(data)
        emotion=data.get("emotion",data.get("emotional_state","neutral"))
        apply_emotion("CHAR_TARA_ROOT",emotion)
        if guardian: apply_emotion("CHAR_GUARDIAN_ROOT",emotion)
        if shadow: apply_emotion("CHAR_SHADOW_ROOT","threat")
        add_star(data)

        start=frame
        end=frame+15
        cam=add_camera(choose_shot(data),idx)
        scene.camera=cam

        # Gentle dolly with protected composition.
        cam.location.x=-1.2 if idx%2 else 1.2
        look_at(cam,(-0.05,0,1.45))
        cam.keyframe_insert("location",frame=start)
        cam.location.x=1.2 if idx%2 else -1.2
        look_at(cam,(0,0,1.45))
        cam.keyframe_insert("location",frame=end)

        # Small character movement for life.
        tara.keyframe_insert("location",frame=start)
        tara.location.x += 0.35
        tara.keyframe_insert("location",frame=end)

        for f in range(start,end+1):
            scene.frame_set(f)
            scene.render.filepath=str(out/f"frame_{f:06d}.png")
            bpy.ops.render.render(write_still=True)
            print(f"[AADWIK VISUAL] FRAME {f}",flush=True)

        frame=end+1

    print(f"[AADWIK VISUAL] COMPLETE: {len(list(out.glob('frame_*.png')))} frames",flush=True)

if __name__=="__main__":
    main()
