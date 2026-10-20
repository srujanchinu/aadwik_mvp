# Aadwik Visual Diagnostic — safe replacement
# Run from the backend folder:
# blender.exe --background --python app\providers\aadwik_visual_diagnostic.py -- --source "generated\aadwik_character_master_v4_sportsuit_fix.blend" --out "generated\reports\aadwik_visual_diagnostics"

import bpy
import sys
import os
from mathutils import Vector

def arg_value(flag, default):
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    try:
        return argv[argv.index(flag) + 1]
    except (ValueError, IndexError):
        return default

source = os.path.abspath(arg_value("--source", "generated/aadwik_character_master_v4_sportsuit_fix.blend"))
out_dir = os.path.abspath(arg_value("--out", "generated/reports/aadwik_visual_diagnostics"))

if not os.path.isfile(source):
    raise FileNotFoundError("Source blend file not found: " + source)

os.makedirs(out_dir, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=source)

scene = bpy.context.scene
original_camera = scene.camera
original_filepath = scene.render.filepath
original_resolution = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
original_engine = scene.render.engine
original_exposure = scene.view_settings.exposure
original_gamma = scene.view_settings.gamma

# Hide Rigify widget meshes from renders only. Do not delete or modify them.
saved_hide_render = {}
for obj in bpy.data.objects:
    if obj.name.startswith("WGT-"):
        saved_hide_render[obj.name] = obj.hide_render
        obj.hide_render = True

# Determine character bounds from visible, non-widget mesh objects.
mesh_objects = [
    obj for obj in scene.objects
    if obj.type == "MESH" and not obj.name.startswith("WGT-")
]
if not mesh_objects:
    raise RuntimeError("No non-widget mesh objects found in the scene.")

coords = []
for obj in mesh_objects:
    try:
        for corner in obj.bound_box:
            coords.append(obj.matrix_world @ Vector(corner))
    except Exception:
        pass
if not coords:
    raise RuntimeError("Could not determine mesh bounds.")

min_x = min(v.x for v in coords)
max_x = max(v.x for v in coords)
min_y = min(v.y for v in coords)
max_y = max(v.y for v in coords)
min_z = min(v.z for v in coords)
max_z = max(v.z for v in coords)
height = max(max_z - min_z, 1.0)
center = Vector(((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2))

# Use a simple temporary diagnostic lighting setup. Nothing is saved to the blend.
created_objects = []
created_data = []

def add_area_light(name, location, energy, size):
    data = bpy.data.lights.new(name=name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((center.x, center.y, center.z + height * 0.62)) - obj.location).to_track_quat("-Z", "Y").to_euler()
    created_objects.append(obj)
    created_data.append(data)

add_area_light("AADWIK_DIAG_Key", (center.x - height * 0.7, center.y - height * 1.0, center.z + height * 0.8), 500, height * 0.65)
add_area_light("AADWIK_DIAG_Fill", (center.x + height * 0.8, center.y - height * 0.8, center.z + height * 0.45), 220, height * 0.7)
add_area_light("AADWIK_DIAG_Rim", (center.x, center.y + height * 0.7, center.z + height * 0.7), 350, height * 0.55)

# Avoid blown-out whites in the face and shirt.
scene.view_settings.exposure = -1.0
scene.view_settings.gamma = 1.0
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False

if scene.world:
    scene.world.color = (0.025, 0.025, 0.025)

def add_camera(name, location, target, ortho_scale):
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new(name, data)
    scene.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    created_objects.append(cam)
    created_data.append(data)
    return cam

# Character is expected to face toward -Y, as in the current Aadwik asset.
front_y = min_y - height * 1.7
back_y = max_y + height * 1.7
side_x = max_x + height * 1.7
face_z = min_z + height * 0.88
face_target = (center.x, center.y, face_z)
face_scale = height * 0.30
body_target = (center.x, center.y, min_z + height * 0.53)
full_scale = height * 1.12

views = [
    ("face_front.png", (center.x, front_y, face_z), face_target, face_scale),
    ("face_three_quarter.png", (center.x + height * 0.75, front_y - height * 0.2, face_z), face_target, face_scale),
    ("legs_front.png", (center.x, front_y, min_z + height * 0.34), (center.x, center.y, min_z + height * 0.34), height * 0.55),
    ("legs_side.png", (side_x, center.y, min_z + height * 0.34), (center.x, center.y, min_z + height * 0.34), height * 0.55),
    ("full_body_front.png", (center.x, front_y, center.z), body_target, full_scale),
]

try:
    for filename, location, target, scale in views:
        cam = add_camera("AADWIK_DIAG_CAMERA_" + filename.replace(".png", ""), location, target, scale)
        scene.camera = cam
        scene.render.filepath = os.path.join(out_dir, filename)
        bpy.ops.render.render(write_still=True)
        print("AADWIK_DIAGNOSTIC_RENDERED:", scene.render.filepath)
finally:
    # Restore in-memory state. This process does not save the .blend file.
    scene.camera = original_camera
    scene.render.filepath = original_filepath
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = original_resolution
    scene.render.engine = original_engine
    scene.view_settings.exposure = original_exposure
    scene.view_settings.gamma = original_gamma
    for name, value in saved_hide_render.items():
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = value

print("AADWIK_VISUAL_DIAGNOSTIC_COMPLETE")
print("Output folder:", out_dir)
print("Source blend was not saved or modified on disk.")
