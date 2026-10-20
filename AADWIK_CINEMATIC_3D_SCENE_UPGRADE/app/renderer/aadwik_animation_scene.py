import bpy
import math
import argparse
from mathutils import Vector

# Aadwik Cinematic 3D Scene Upgrade
# Blender 5.2-safe, dependency-free, no Pillow.
# Story baseline:
# "A curious girl discovers a glowing blue star in a moonlit forest
#  and helps a tiny guardian return home."

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes, bpy.data.curves, bpy.data.materials,
        bpy.data.cameras, bpy.data.lights
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

def mat(name, color, metallic=0.0, roughness=0.6, emission=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = strength
    return m

def sphere(name, loc, scale, material, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=rings, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return o

def cube(name, loc, scale, material, bevel=0.12):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Soft edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    return o

def cylinder(name, loc, radius, depth, material):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=radius, depth=depth, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    return o

def cone(name, loc, radius, depth, material):
    bpy.ops.mesh.primitive_cone_add(
        vertices=24, radius1=radius, radius2=0.0,
        depth=depth, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    return o

def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

def parent(root, *children):
    for child in children:
        child.parent = root

def build_tara():
    skin = mat("Tara_Skin", (0.55, 0.23, 0.12), roughness=0.75)
    hair = mat("Tara_Hair", (0.025, 0.012, 0.006), roughness=0.9)
    dress = mat("Tara_Dress", (0.06, 0.20, 0.62), roughness=0.72)
    shoe = mat("Tara_Shoes", (0.035, 0.025, 0.02), roughness=0.8)
    eye = mat("Tara_Eyes", (0.015, 0.008, 0.004), roughness=0.35)

    root = bpy.data.objects.new("Tara", None)
    bpy.context.collection.objects.link(root)
    root["character_id"] = "char_tara_cinematic_v1"
    root["identity_locked"] = True

    body = sphere("Tara_Body", (-1.55, 0, 1.05), (0.50, 0.36, 0.78), dress)
    head = sphere("Tara_Head", (-1.55, -0.01, 2.05), (0.43, 0.38, 0.43), skin)
    haircap = sphere("Tara_Hair", (-1.55, 0.02, 2.31), (0.46, 0.40, 0.25), hair)
    eye1 = sphere("Tara_Eye_L", (-1.72, -0.36, 2.10), (0.055, 0.035, 0.065), eye)
    eye2 = sphere("Tara_Eye_R", (-1.38, -0.36, 2.10), (0.055, 0.035, 0.065), eye)
    arm1 = cylinder("Tara_Arm_L", (-2.02, 0, 1.18), 0.12, 0.75, skin)
    arm1.rotation_euler[1] = math.radians(24)
    arm2 = cylinder("Tara_Arm_R", (-1.08, 0, 1.18), 0.12, 0.75, skin)
    arm2.rotation_euler[1] = math.radians(-24)
    leg1 = cylinder("Tara_Leg_L", (-1.78, 0, 0.36), 0.13, 0.72, skin)
    leg2 = cylinder("Tara_Leg_R", (-1.32, 0, 0.36), 0.13, 0.72, skin)
    foot1 = sphere("Tara_Foot_L", (-1.80, -0.10, 0.02), (0.22, 0.30, 0.11), shoe)
    foot2 = sphere("Tara_Foot_R", (-1.30, -0.10, 0.02), (0.22, 0.30, 0.11), shoe)
    parent(root, body, head, haircap, eye1, eye2, arm1, arm2, leg1, leg2, foot1, foot2)
    return root

def build_guardian():
    glow = mat("Guardian_Glow", (0.12, 0.55, 1.0), metallic=0.25, roughness=0.28,
               emission=(0.03, 0.22, 1.0), strength=1.5)
    dark = mat("Guardian_Dark", (0.015, 0.035, 0.09), roughness=0.5)
    eye = mat("Guardian_Eyes", (0.35, 0.85, 1.0), emission=(0.2, 0.7, 1.0), strength=3.0)

    root = bpy.data.objects.new("Guardian", None)
    bpy.context.collection.objects.link(root)
    root["character_id"] = "char_guardian_cinematic_v1"
    root["identity_locked"] = True

    body = sphere("Guardian_Body", (1.0, 0, 0.82), (0.38, 0.32, 0.50), glow)
    head = sphere("Guardian_Head", (1.0, -0.02, 1.48), (0.34, 0.30, 0.34), dark)
    eye1 = sphere("Guardian_Eye_L", (0.88, -0.28, 1.54), (0.075, 0.035, 0.055), eye)
    eye2 = sphere("Guardian_Eye_R", (1.12, -0.28, 1.54), (0.075, 0.035, 0.055), eye)
    ear1 = cone("Guardian_Ear_L", (0.76, 0, 1.84), 0.14, 0.38, glow)
    ear2 = cone("Guardian_Ear_R", (1.24, 0, 1.84), 0.14, 0.38, glow)
    arm1 = cylinder("Guardian_Arm_L", (0.63, 0, 0.90), 0.09, 0.45, glow)
    arm2 = cylinder("Guardian_Arm_R", (1.37, 0, 0.90), 0.09, 0.45, glow)
    parent(root, body, head, eye1, eye2, ear1, ear2, arm1, arm2)
    return root

def build_star():
    blue = mat("Blue_Star", (0.03, 0.30, 1.0), metallic=0.15, roughness=0.2,
               emission=(0.03, 0.30, 1.0), strength=7.0)
    star = sphere("Blue_Star", (0.0, 0.0, 3.10), (0.23, 0.23, 0.23), blue)
    star["prop_id"] = "prop_blue_star_cinematic_v1"
    return star

def build_environment():
    ground = mat("Moonlit_Ground", (0.015, 0.035, 0.025), roughness=1.0)
    trunk = mat("Tree_Trunk", (0.055, 0.025, 0.012), roughness=0.95)
    leaves = mat("Tree_Leaves", (0.015, 0.09, 0.045), roughness=0.9)
    rockmat = mat("Rocks", (0.08, 0.09, 0.11), roughness=0.95)

    cube("Forest_Ground", (0, 1.5, -0.18), (8, 7, 0.18), ground, 0.05)

    # Framing trees: broad trunks + clustered foliage.
    positions = [(-5, 3), (-4, 7), (-2.8, 8), (3.2, 7), (4.8, 4), (5.4, 8), (2.8, 11), (-4.5, 11)]
    for i, (x, y) in enumerate(positions):
        h = 4.0 + (i % 3) * 0.8
        cylinder(f"Tree_Trunk_{i}", (x, y, h/2-0.1), 0.34, h, trunk)
        for j in range(3):
            sphere(
                f"Tree_Crown_{i}_{j}",
                (x + (j-1)*0.55, y, h + 0.45 + (j%2)*0.35),
                (1.25, 1.0, 1.05),
                leaves
            )

    for i, (x, y, s) in enumerate([(-3.5,1.5,.55),(3.4,2,.7),(-2.7,4,.45),(2.8,5,.5)]):
        sphere(f"Rock_{i}", (x,y,s*0.35), (s, s*0.75, s*0.45), rockmat)

def add_lights():
    world = bpy.context.scene.world
    world.color = (0.003, 0.006, 0.015)
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.003, 0.006, 0.018, 1.0)
        bg.inputs["Strength"].default_value = 0.12

    bpy.ops.object.light_add(type="AREA", location=(0, -2.5, 6))
    key = bpy.context.object
    key.name = "Moon_Key"
    key.data.energy = 850
    key.data.shape = "DISK"
    key.data.size = 5.0
    key.data.color = (0.35, 0.48, 1.0)
    look_at(key, (0, 2, 1.2))

    bpy.ops.object.light_add(type="AREA", location=(-4, -1, 3.5))
    fill = bpy.context.object
    fill.name = "Soft_Fill"
    fill.data.energy = 500
    fill.data.size = 4.0
    fill.data.color = (0.7, 0.8, 1.0)
    look_at(fill, (-1, 1, 1.3))

    bpy.ops.object.light_add(type="POINT", location=(0, 0, 3.1))
    starlight = bpy.context.object
    starlight.name = "Star_Glow"
    starlight.data.energy = 850
    starlight.data.color = (0.05, 0.35, 1.0)
    starlight.data.shadow_soft_size = 1.2

def setup_camera(width, height):
    bpy.ops.object.camera_add(location=(0, -11, 3.2))
    cam = bpy.context.object
    cam.name = "Camera"
    cam.data.lens = 48
    cam.data.sensor_width = 36
    look_at(cam, (0, 1.8, 1.35))
    bpy.context.scene.camera = cam
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    return cam

def animate(root, start, end, x0, x1):
    root.location = (x0, 0, 0)
    root.keyframe_insert("location", frame=start, index=0)
    root.location = (x1, 0, 0)
    root.keyframe_insert("location", frame=end, index=0)

def animate_star(star, start, end):
    star.location.z = 3.10
    star.keyframe_insert("location", frame=start, index=2)
    star.location.z = 3.45
    star.keyframe_insert("location", frame=(start+end)//2, index=2)
    star.location.z = 3.10
    star.keyframe_insert("location", frame=end, index=2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames_dir", required=True)
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--height", type=int, default=360)
    ap.add_argument("--fps", type=int, default=8)
    ap.add_argument("--frames", type=int, default=128)
    ap.add_argument("--prompt", default="")
    # Blender passes its own command-line arguments before the "--" separator.
    # Only parse the arguments intended for this scene script.
    import sys
    blender_argv = sys.argv
    script_argv = blender_argv[blender_argv.index("--") + 1:] if "--" in blender_argv else []
    args = ap.parse_args(script_argv)

    clear_scene()
    build_environment()
    tara = build_tara()
    guardian = build_guardian()
    star = build_star()
    add_lights()
    cam = setup_camera(args.width, args.height)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.fps = args.fps
    scene.render.film_transparent = False
    scene.frame_start = 1
    scene.frame_end = args.frames

    # Subtle character motion across the shot.
    animate(tara, 1, args.frames, -0.25, 0.65)
    animate(guardian, 1, args.frames, 0.55, -0.55)
    animate_star(star, 1, args.frames)

    out = args.frames_dir
    import os
    os.makedirs(out, exist_ok=True)

    for frame in range(1, args.frames + 1):
        scene.frame_set(frame)

        # Slow cinematic camera push + story framing.
        t = (frame - 1) / max(1, args.frames - 1)
        cam.location.x = 0.15 * math.sin(t * math.pi)
        cam.location.y = -11.0 + 0.8 * t
        cam.location.z = 3.15 + 0.12 * math.sin(t * math.pi)
        look_at(cam, (0.0, 1.7, 1.45))

        scene.render.filepath = os.path.join(out, f"frame_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    main()
