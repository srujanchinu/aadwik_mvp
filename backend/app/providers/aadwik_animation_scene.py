import argparse
from pathlib import Path
import bpy
from mathutils import Vector


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        pass


def mat(name, color, metallic=0.0, roughness=0.7):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m


def uv_sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return o


def cube(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new("SoftEdges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    o.data.materials.append(material)
    return o


def build_tara():
    skin = mat("TaraSkin", (0.82, 0.50, 0.30), roughness=0.8)
    hair = mat("TaraHair", (0.08, 0.035, 0.015), roughness=0.9)
    dress = mat("TaraDress", (0.12, 0.30, 0.72), roughness=0.75)
    root = bpy.data.objects.new("Tara", None)
    bpy.context.collection.objects.link(root)
    body = uv_sphere("TaraBody", (-1.7, 0, 1.0), (0.48, 0.34, 0.75), dress)
    head = uv_sphere("TaraHead", (-1.7, 0, 2.05), (0.43, 0.38, 0.43), skin)
    hair_o = uv_sphere("TaraHair", (-1.7, -0.02, 2.34), (0.45, 0.40, 0.25), hair)
    for o in (body, head, hair_o):
        o.parent = root
    return root


def build_guardian():
    glow = mat("GuardianGlow", (0.25, 0.65, 1.0), metallic=0.15, roughness=0.35)
    dark = mat("GuardianDark", (0.05, 0.12, 0.25), roughness=0.55)
    root = bpy.data.objects.new("Guardian", None)
    bpy.context.collection.objects.link(root)
    body = uv_sphere("GuardianBody", (1.0, 0, 0.9), (0.36, 0.30, 0.48), glow)
    head = uv_sphere("GuardianHead", (1.0, 0, 1.58), (0.32, 0.28, 0.32), dark)
    for o in (body, head):
        o.parent = root
    return root


def build_star():
    blue = mat("BlueStar", (0.05, 0.35, 1.0), metallic=0.2, roughness=0.25)
    return uv_sphere("BlueStar", (0.0, 0.0, 3.05), (0.22, 0.22, 0.22), blue)


def animate(root, start, end, x0, x1):
    root.location = (x0, 0, 0)
    root.keyframe_insert("location", frame=start, index=0)
    root.location = (x1, 0, 0)
    root.keyframe_insert("location", frame=end, index=0)


def setup_world():
    world = bpy.context.scene.world
    world.color = (0.005, 0.008, 0.02)
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.004, 0.008, 0.025, 1)
        bg.inputs["Strength"].default_value = 0.22


def setup_camera():
    bpy.ops.object.camera_add(location=(0, -10, 3.0))
    cam = bpy.context.object
    cam.name = "Camera"
    cam.data.lens = 48
    bpy.context.scene.camera = cam
    return cam


def setup_lights():
    bpy.ops.object.light_add(type="AREA", location=(0, -2, 5))
    key = bpy.context.object
    key.data.energy = 850
    key.data.shape = "DISK"
    key.data.size = 5
    key.rotation_euler = (0.25, 0, 0)

    bpy.ops.object.light_add(type="POINT", location=(0, 0, 3))
    fill = bpy.context.object
    fill.data.energy = 450
    fill.data.color = (0.25, 0.5, 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames_dir", required=True)
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--height", type=int, default=360)
    ap.add_argument("--fps", type=int, default=8)
    ap.add_argument("--frames", type=int, default=128)
    ap.add_argument("--prompt", default="")
    # Blender 5.2 may expose script arguments differently through sys.argv.
    # Explicitly parse only the arguments after Blender's "--" separator.
    import sys
    raw_argv = sys.argv
    if "--" in raw_argv:
        raw_argv = raw_argv[raw_argv.index("--") + 1:]
    args = ap.parse_args(raw_argv)

    clear()
    setup_world()
    setup_camera()
    setup_lights()

    ground = mat("Ground", (0.025, 0.055, 0.035), roughness=1.0)
    cube("Ground", (0, 0, -0.25), (5, 5, 0.25), ground)

    tara = build_tara()
    guardian = build_guardian()
    star = build_star()

    animate(tara, 1, args.frames, -1.2, 1.2)
    animate(guardian, 1, args.frames, 1.2, -0.5)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.fps = args.fps
    scene.render.film_transparent = False

    out = Path(args.frames_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Eight shot ranges, producing one continuous numbered frame sequence.
    for frame in range(1, args.frames + 1):
        scene.frame_set(frame)
        scene.render.filepath = str(out / f"frame_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
