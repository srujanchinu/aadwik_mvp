import bpy
import sys
import os
from pathlib import Path
from mathutils import Vector

print("\n[AADWIK MPFB AUTO V2] START")

# Find the MPFB source package even when Blender's background Python
# has not exposed "mpfb" on sys.path.
search_roots = [
    Path(os.environ.get("APPDATA", "")) / "Blender Foundation" / "Blender" / "5.2",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Blender Foundation" / "Blender" / "5.2",
    Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Roaming" / "Blender Foundation" / "Blender" / "5.2",
    Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "Blender Foundation" / "Blender" / "5.2",
]

mpfb_package = None
for root in search_roots:
    if not root.exists():
        continue
    try:
        matches = list(root.rglob("assetservice.py"))
    except Exception:
        matches = []
    for p in matches:
        if p.parent.name == "services" and p.parent.parent.name == "mpfb":
            mpfb_package = p.parent.parent
            break
    if mpfb_package:
        break

if mpfb_package is None:
    # Fall back to Blender's extension/addon search paths.
    candidates = []
    for base in bpy.utils.script_paths():
        candidates += [
            Path(base) / "addons" / "mpfb",
            Path(base) / "addons_core" / "mpfb",
            Path(base) / "extensions" / "mpfb",
        ]
    for p in candidates:
        if (p / "services" / "assetservice.py").exists():
            mpfb_package = p
            break

if mpfb_package is None:
    raise RuntimeError(
        "MPFB is enabled (its operators work), but its Python package path "
        "could not be located automatically."
    )

mpfb_parent = str(mpfb_package.parent)
if mpfb_parent not in sys.path:
    sys.path.insert(0, mpfb_parent)

print(f"[AADWIK MPFB AUTO V2] MPFB PATH: {mpfb_package}")

from mpfb.services.assetservice import AssetService

human = bpy.data.objects.get("Human")
if human is None:
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("No MPFB Human mesh found.")
    human = meshes[0]

bpy.ops.object.select_all(action="DESELECT")
human.select_set(True)
bpy.context.view_layer.objects.active = human

# Make sure MPFB has refreshed its installed asset lists.
AssetService.update_all_asset_lists()

if not AssetService.system_assets_pack_is_installed():
    raise RuntimeError("MPFB still reports MakeHuman System Assets as not installed.")

hairs = AssetService.get_asset_list("hair", "mhclo")
print(f"[AADWIK MPFB AUTO V2] HAIR ASSETS FOUND: {len(hairs)}")

if not hairs:
    raise RuntimeError(
        "System assets are installed, but no hair assets are visible. "
        "The downloaded pack may not contain the hair library."
    )

# Prefer Bob01/Bob02 because they are visible in the user's MPFB Hair library.
selected = None
for wanted in ("Bob01", "Bob02", "Bob03", "Bob04", "Bob05"):
    for label, info in hairs.items():
        if wanted.lower() in str(label).lower():
            selected = (label, info)
            break
    if selected:
        break

if selected is None:
    selected = next(iter(hairs.items()))

hair_label, hair_info = selected
hair_path = str(hair_info["full_path"])

print(f"[AADWIK MPFB AUTO V2] HAIR SELECTED: {hair_label}")
print(f"[AADWIK MPFB AUTO V2] HAIR FILE: {hair_path}")

# Add the standard MPFB rig if none exists.
if not any(o.type == "ARMATURE" for o in bpy.data.objects):
    print("[AADWIK MPFB AUTO V2] ADDING STANDARD RIG")
    result = bpy.ops.mpfb.add_standard_rig()
    print(f"[AADWIK MPFB AUTO V2] RIG RESULT: {result}")

bpy.ops.object.select_all(action="DESELECT")
human.select_set(True)
bpy.context.view_layer.objects.active = human

# MPFB's documented hair/clothes operator.
result = bpy.ops.mpfb.load_library_clothes(filepath=hair_path)
print(f"[AADWIK MPFB AUTO V2] HAIR LOAD RESULT: {result}")

# Smooth all meshes.
for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True

# Automatic camera.
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.visible_get()]
corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
min_v = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
max_v = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
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

# Ground.
ground = bpy.data.objects.get("AADWIK_AUTO_GROUND")
if ground is None:
    bpy.ops.mesh.primitive_plane_add(size=30, location=(center.x, center.y, min_v.z))
    ground = bpy.context.object
    ground.name = "AADWIK_AUTO_GROUND"

mat = bpy.data.materials.get("AADWIK_AUTO_GROUND_MAT")
if mat is None:
    mat = bpy.data.materials.new("AADWIK_AUTO_GROUND_MAT")
    mat.diffuse_color = (0.055, 0.065, 0.08, 1)
ground.data.materials.clear()
ground.data.materials.append(mat)

def add_area(name, loc, energy, size):
    obj = bpy.data.objects.get(name)
    if obj is None:
        ld = bpy.data.lights.new(name + "_DATA", "AREA")
        obj = bpy.data.objects.new(name, ld)
        bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.data.energy = energy
    obj.data.shape = "DISK"
    obj.data.size = size
    obj.rotation_euler = (center - obj.location).to_track_quat("-Z", "Y").to_euler()

add_area("AADWIK_KEY", center + Vector((2.8, -4, height*0.9)), 900, 3)
add_area("AADWIK_FILL", center + Vector((-3, -2.5, height*0.65)), 500, 3.5)
add_area("AADWIK_RIM", center + Vector((1.5, 2.5, height)), 800, 2.5)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 700
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

base = Path(bpy.data.filepath).parent
blend_out = base / "aadwik_maya_base_v1_AUTO_HAIR_V2.blend"
png_out = base / "aadwik_maya_base_v1_AUTO_HAIR_V2.png"

bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))
scene.render.filepath = str(png_out)
bpy.ops.render.render(write_still=True)

print("\n[AADWIK MPFB AUTO V2] COMPLETE")
print(f"[AADWIK MPFB AUTO V2] HAIR: {hair_label}")
print(f"[AADWIK MPFB AUTO V2] BLEND: {blend_out}")
print(f"[AADWIK MPFB AUTO V2] PREVIEW: {png_out}")
