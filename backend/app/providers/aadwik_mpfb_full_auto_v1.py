import bpy
from pathlib import Path
from mathutils import Vector

print("\n[AADWIK MPFB AUTO] START")

human = bpy.data.objects.get("Human")
if human is None:
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("No MPFB human mesh found.")
    human = meshes[0]

bpy.ops.object.select_all(action="DESELECT")
human.select_set(True)
bpy.context.view_layer.objects.active = human

scene = bpy.context.scene

# MPFB loading settings
for prop, value in {
    "ASLS_fit_to_body": True,
    "ASLS_mask_base_mesh": True,
    "ASLS_delete_group": True,
    "ASLS_specific_delete_group": True,
    "ASLS_interpolate_weights": True,
    "ASLS_import_subrig": True,
    "ASLS_import_weights": True,
    "ASLS_add_subdiv_modifier": True,
    "ASLS_subdiv_levels": 2,
    "ASLS_clothes_type": "MAKESKIN",
    "ASLS_eyes_type": "PROCEDURAL_EYES",
}.items():
    if hasattr(scene, prop):
        try:
            setattr(scene, prop, value)
        except Exception:
            pass

# Add MPFB standard rig if needed
if not any(o.type == "ARMATURE" for o in bpy.data.objects):
    print("[AADWIK MPFB AUTO] Adding standard rig...")
    try:
        bpy.ops.mpfb.add_standard_rig()
        print("[AADWIK MPFB AUTO] STANDARD RIG: OK")
    except Exception as e:
        print(f"[AADWIK MPFB AUTO] STANDARD RIG SKIPPED: {e}")

bpy.ops.object.select_all(action="DESELECT")
human.select_set(True)
bpy.context.view_layer.objects.active = human

# Find installed hair automatically, preferring Bob styles
from mpfb.services.assetservice import AssetService
hairs = AssetService.get_asset_list("hair", "mhclo")
if not hairs:
    raise RuntimeError("No installed MPFB hair assets found.")

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
hair_path = hair_info["full_path"]
print(f"[AADWIK MPFB AUTO] HAIR: {hair_label}")
print(f"[AADWIK MPFB AUTO] FILE: {hair_path}")

# Load through the official MPFB hair/clothes library operator
result = bpy.ops.mpfb.load_library_clothes(filepath=str(hair_path))
print(f"[AADWIK MPFB AUTO] HAIR LOAD: {result}")

# Smooth meshes
for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True

# Automatic camera framing
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
scene.camera = camera

# Ground
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

def area(name, loc, energy, size):
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

area("AADWIK_KEY", center + Vector((2.8, -4, height*0.9)), 900, 3)
area("AADWIK_FILL", center + Vector((-3, -2.5, height*0.65)), 500, 3.5)
area("AADWIK_RIM", center + Vector((1.5, 2.5, height)), 800, 2.5)

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 700
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

base = Path(bpy.data.filepath).parent
blend_out = base / "aadwik_maya_base_v1_AUTO_HAIR.blend"
png_out = base / "aadwik_maya_base_v1_AUTO_HAIR.png"

bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))
scene.render.filepath = str(png_out)
bpy.ops.render.render(write_still=True)

print("[AADWIK MPFB AUTO] COMPLETE")
print(f"[AADWIK MPFB AUTO] BLEND: {blend_out}")
print(f"[AADWIK MPFB AUTO] PREVIEW: {png_out}")
