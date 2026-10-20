"""
AADWIK visual diagnostic renderer
Blender 5.2.x. Opens the saved character and renders front/side diagnostic views.
It does not edit or save the source .blend. It only writes PNGs to the report folder.
"""
import bpy
import sys
import os
import math
from mathutils import Vector, Quaternion

DEFAULT_SOURCE = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v4_sportsuit_fix.blend"
DEFAULT_OUT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\reports\aadwik_visual_diagnostics"

def get_args():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--source", default=DEFAULT_SOURCE)
    p.add_argument("--out", default=DEFAULT_OUT)
    p.add_argument("--resolution", type=int, default=900)
    return p.parse_args(argv)

def log(s):
    print("[AADWIK VISUAL DIAGNOSTIC] " + str(s), flush=True)

def world_bounds(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return (
        Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
        Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))),
    )

def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

def make_camera(name, location, target, ortho_scale):
    data = bpy.data.cameras.new(name + "_DATA")
    cam = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = location
    point_at(cam, target)
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
    data.lens = 50
    return cam

def main():
    args = get_args()
    src = os.path.abspath(args.source)
    out = os.path.abspath(args.out)
    if not os.path.isfile(src):
        raise FileNotFoundError("Character blend not found: " + src)
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=src)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES" if "CYCLES" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys() else scene.render.engine
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = args.resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100

    # Only real character meshes; Rigify WGT widgets are deliberately excluded.
    candidates = [
        o for o in bpy.data.objects
        if o.type == "MESH" and not o.name.startswith("WGT-")
        and (o.name == "Human" or o.name.startswith("Human."))
    ]
    if not candidates:
        candidates = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("WGT-")]
    if not candidates:
        raise RuntimeError("No non-widget character meshes found.")

    mins = [float("inf")] * 3
    maxs = [float("-inf")] * 3
    for obj in candidates:
        lo, hi = world_bounds(obj)
        for i in range(3):
            mins[i] = min(mins[i], lo[i])
            maxs[i] = max(maxs[i], hi[i])
    lo = Vector(mins)
    hi = Vector(maxs)
    center = (lo + hi) * 0.5
    height = max(hi.z - lo.z, 1.0)
    width = max(hi.x - lo.x, 0.5)
    depth = max(hi.y - lo.y, 0.5)

    # Temporarily hide Rigify widget meshes in render, never deleting them.
    hidden = []
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name.startswith("WGT-"):
            hidden.append((obj, obj.hide_render))
            obj.hide_render = True

    # Diagnostic lighting. Added only in the opened in-memory scene.
    def area(name, loc, power, size, target):
        d = bpy.data.lights.new(name, "AREA")
        o = bpy.data.objects.new(name, d)
        scene.collection.objects.link(o)
        o.location = loc
        d.energy = power
        d.shape = "DISK"
        d.size = size
        point_at(o, target)
    area("AADWIK_DIAG_KEY", (center.x + height*0.25, center.y - height*0.7, center.z + height*0.35), 1200, height*0.55, center)
    area("AADWIK_DIAG_FILL", (center.x - height*0.4, center.y - height*0.5, center.z + height*0.05), 700, height*0.6, center)
    area("AADWIK_DIAG_RIM", (center.x, center.y + height*0.6, center.z + height*0.3), 1000, height*0.45, center)

    if scene.world is None:
        scene.world = bpy.data.worlds.new("AADWIK_DIAGNOSTIC_WORLD")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.08, 0.08, 0.08, 1)
        bg.inputs["Strength"].default_value = 0.5

    # Use bounds to place cameras. Blender characters commonly face -Y.
    face_z = lo.z + height * 0.88
    face_target = (center.x, center.y, face_z)
    face_scale = max(height * 0.28, 0.5)
    leg_target = (center.x, center.y, lo.z + height * 0.34)
    leg_scale = max(height * 0.58, 1.0)
    distance = max(height * 1.8, 3.0)

    views = [
        ("face_front.png", (center.x, center.y - distance, face_z), face_target, face_scale),
        ("face_three_quarter.png", (center.x + distance*0.65, center.y - distance*0.8, face_z), face_target, face_scale),
        ("legs_front.png", (center.x, center.y - distance, leg_target[2]), leg_target, leg_scale),
        ("legs_side.png", (center.x + distance, center.y, leg_target[2]), leg_target, leg_scale),
        ("full_body_front.png", (center.x, center.y - distance*1.4, center.z), center, height*1.18),
    ]

    original_camera = scene.camera
    original_filepath = scene.render.filepath
    try:
        for filename, loc, target, scale in views:
            cam = make_camera("AADWIK_DIAG_CAMERA_" + filename.replace(".png", ""), loc, target, scale)
            cam.data.ortho_scale = scale
            scene.camera = cam
            scene.render.filepath = os.path.join(out, filename)
            log("Rendering " + filename)
            bpy.ops.render.render(write_still=True)
            bpy.data.objects.remove(cam, do_unlink=True)
            bpy.data.cameras.remove(cam.data)
    finally:
        scene.camera = original_camera
        scene.render.filepath = original_filepath
        for obj, was_hidden in hidden:
            obj.hide_render = was_hidden

    log("COMPLETE. Source .blend was not saved or modified.")
    log("Images: " + out)

if __name__ == "__main__":
    main()
