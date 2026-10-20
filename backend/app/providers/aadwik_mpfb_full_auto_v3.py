import bpy
import os
from pathlib import Path
from mathutils import Vector

print("\n[AADWIK MPFB AUTO V3] START")

# ------------------------------------------------------------
# Find the current MPFB human
# ------------------------------------------------------------
human = bpy.data.objects.get("Human")
if human is None:
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("No MPFB human mesh found.")
    human = meshes[0]

bpy.ops.object.select_all(action="DESELECT")
human.select_set(True)
bpy.context.view_layer.objects.active = human

# ------------------------------------------------------------
# Find installed hair files WITHOUT importing MPFB internals
# ------------------------------------------------------------
roots = [
    Path(os.environ.get("APPDATA", "")) / "Blender Foundation" / "Blender" / "5.2",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Blender Foundation" / "Blender" / "5.2",
]

hair_files = []

for root in roots:
    if not root.exists():
        continue
    try:
        for ext in root.rglob("*.mhclo"):
            p = str(ext).lower()
            if "\\hair\\" in p or "/hair/" in p:
                hair_files.append(ext)
    except Exception:
        pass

# Remove duplicates
unique = {}
for p in hair_files:
    unique[str(p).lower()] = p
hair_files = list(unique.values())

print(f"[AADWIK MPFB AUTO V3] HAIR FILES FOUND: {len(hair_files)}")

if not hair_files:
    raise RuntimeError(
        "No .mhclo hair files were found. The system asset pack may be installed "
        "but Blender's extension asset location needs to be identified."
    )

# Prefer a Bob hairstyle
preferred = None
for p in hair_files:
    name = p.stem.lower()
    if "bob" in name:
        preferred = p
        break

hair_file = preferred or hair_files[0]

print(f"[AADWIK MPFB AUTO V3] SELECTED HAIR: {hair_file}")

# ------------------------------------------------------------
# Use MPFB's exposed operator only.
# We deliberately do NOT import mpfb.services.*
# ------------------------------------------------------------
if not hasattr(bpy.ops.mpfb, "load_library_clothes"):
    raise RuntimeError(
        "MPFB load_library_clothes operator is not available in this Blender session."
    )

result = bpy.ops.mpfb.load_library_clothes(filepath=str(hair_file))
print(f"[AADWIK MPFB AUTO V3] MPFB HAIR LOAD: {result}")

# ------------------------------------------------------------
# Smooth meshes
# ------------------------------------------------------------
for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True

# ------------------------------------------------------------
# Automatic camera
# ------------------------------------------------------------
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.visible_get()]
corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]

min_v = Vector((
    min(v.x for v in corners),
    min(v.y for v in corners),
    min(v.z for v in corners),
))
max_v = Vector((
    max(v.x for v in corners),
    max(v.y for v in corners),
    max(v.z for v in corners),
))

center = (min_v + max_v) * 0.5
height = max_v.z - min_v.z

camera = bpy.data.objects.get("AADWIK_AUTO_CAMERA")
if camera is None:
    data = bpy.data.cameras.new("AADWIK_AUTO_CAMERA_DATA")
    camera = bpy.data.objects.new("AADWIK_AUTO_CAMERA", data)
    bpy.context.collection.objects.link(camera)

camera.data.lens = 58
camera.data.sensor_width = 36
camera.location = center + Vector((0, -max(height * 1.55, 2.4), height * 0.08))
camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = camera

# ------------------------------------------------------------
# Save + render
# ------------------------------------------------------------
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 700
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

base = Path(bpy.data.filepath).parent
blend_out = base / "aadwik_maya_base_v1_AUTO_HAIR_V3.blend"
png_out = base / "aadwik_maya_base_v1_AUTO_HAIR_V3.png"

bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))
scene.render.filepath = str(png_out)
bpy.ops.render.render(write_still=True)

print("\n[AADWIK MPFB AUTO V3] COMPLETE")
print(f"[AADWIK MPFB AUTO V3] HAIR: {hair_file}")
print(f"[AADWIK MPFB AUTO V3] BLEND: {blend_out}")
print(f"[AADWIK MPFB AUTO V3] PREVIEW: {png_out}")
