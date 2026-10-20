
import bpy
import sys
import os
import math
import traceback
from pathlib import Path
from mathutils import Vector

# ------------------------------------------------------------
# AADWIK RIGIFY CHARACTER TEST V1
# Maya V3 -> Human Metarig -> Rigify -> Skinning -> Pose Test
# This script DOES NOT touch Aadwik's movie pipeline.
# ------------------------------------------------------------

print("[AADWIK RIGIFY] CHARACTER TEST V1 START")

def get_arg(name, default=None):
    argv = sys.argv
    if "--" not in argv:
        return default
    argv = argv[argv.index("--") + 1:]
    for i, a in enumerate(argv):
        if a == name and i + 1 < len(argv):
            return argv[i + 1]
    return default

source_script = get_arg("--source")
blend_out = get_arg("--blend_out", "//aadwik_rigify_v1.blend")
render_out = get_arg("--render_out", "//aadwik_rigify_v1.png")

if not source_script or not os.path.exists(source_script):
    raise RuntimeError("Missing --source V3 script: " + str(source_script))

# -----------------------------
# Enable Rigify
# -----------------------------
try:
    import addon_utils
    addon_utils.enable("rigify", default_set=False, persistent=False)
    print("[AADWIK RIGIFY] Rigify addon enabled")
except Exception as e:
    print("[AADWIK RIGIFY] WARNING: could not enable Rigify:", e)

# -----------------------------
# Run Maya V3 source builder
# -----------------------------
print("[AADWIK RIGIFY] Loading character source:", source_script)

# Make source script believe it is being run by Blender normally.
source_code = Path(source_script).read_text(encoding="utf-8")
source_globals = {
    "__name__": "__aadwik_maya_v3_source__",
    "__file__": source_script,
}
exec(compile(source_code, source_script, "exec"), source_globals, source_globals)

# If source script has a main(), don't call it automatically unless
# the script itself did not already construct the character.
print("[AADWIK RIGIFY] Source executed")

# -----------------------------
# Identify character geometry
# -----------------------------
mesh_objects = [
    o for o in bpy.context.scene.objects
    if o.type == "MESH"
    and not o.name.startswith(("Rigify", "WGT-", "DEF-", "ORG-", "MCH-"))
]

if not mesh_objects:
    raise RuntimeError("No character mesh objects found after Maya V3 source execution.")

# Put character in a predictable centered location and measure bounds.
all_world = []
for obj in mesh_objects:
    for c in obj.bound_box:
        all_world.append(obj.matrix_world @ Vector(c))

min_v = Vector((
    min(v.x for v in all_world),
    min(v.y for v in all_world),
    min(v.z for v in all_world),
))
max_v = Vector((
    max(v.x for v in all_world),
    max(v.y for v in all_world),
    max(v.z for v in all_world),
))

center = (min_v + max_v) * 0.5
height = max_v.z - min_v.z
width = max_v.x - min_v.x
depth = max_v.y - min_v.y

print(f"[AADWIK RIGIFY] Character bounds H={height:.3f} W={width:.3f} D={depth:.3f}")

# Move whole character so feet are near Z=0 and X/Y centered.
for obj in mesh_objects:
    obj.location.x -= center.x
    obj.location.y -= center.y
    obj.location.z -= min_v.z

# Recalculate bounds after normalization.
bpy.context.view_layer.update()

# -----------------------------
# -----------------------------
# Add Blender Human Metarig
# -----------------------------
for obj in list(bpy.data.objects):
    if (
        obj.name in {"metarig", "rig"}
        or obj.name.startswith("rigify_rig")
    ):
        bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")

# Rigify human metarig
bpy.ops.object.armature_human_metarig_add()

metarig = bpy.context.object

if metarig is None or metarig.type != "ARMATURE":
    raise RuntimeError(
        "[AADWIK RIGIFY] Failed to create human metarig."
    )

metarig.name = "AADWIK_MAYA_METARIG_V1"
metarig.location = (0.0, 0.0, 0.0)

print("[AADWIK RIGIFY] Human metarig created")
print("[AADWIK RIGIFY] METARIG:", metarig.name)

# Blender/Rigify assumes ~2m human scale. Scale metarig to character height.
if height > 0.001:
    scale = height / 2.0
    metarig.scale = (scale, scale, scale)
    bpy.context.view_layer.update()

# Character is centered on Z=0 after normalization.
# Human metarig should have its feet at ground and body centered.
# Move metarig so its lowest bone point approximately matches ground.
zs = []
for b in metarig.data.bones:
    zs.extend([b.head_local.z, b.tail_local.z])
if zs:
    metarig.location.z -= min(zs) * scale

bpy.context.view_layer.update()

# -----------------------------
# Match key human metarig bones
# -----------------------------
# This is intentionally conservative. Rigify's official workflow requires
# matching metarig bones to the character before generation.
# We use measured character proportions rather than pretending automatic
# inference is perfect.
bpy.context.view_layer.objects.active = metarig
metarig.select_set(True)

# Save a copy of the pre-generation state.
pre_path = str(Path(blend_out).with_name(Path(blend_out).stem + "_METARIG.blend"))
bpy.ops.wm.save_as_mainfile(filepath=pre_path)
print("[AADWIK RIGIFY] Metarig checkpoint:", pre_path)

# -----------------------------
# Generate Rigify rig
# -----------------------------
try:
    bpy.context.view_layer.objects.active = metarig
    metarig.select_set(True)
    bpy.ops.object.mode_set(mode="OBJECT")
except:
    pass

generated = False
for op_name in ("rigify_generate",):
    try:
        op = getattr(bpy.ops.pose, op_name)
        op()
        generated = True
        break
    except Exception as e:
        print("[AADWIK RIGIFY] Generate attempt failed:", repr(e))

if not generated:
    print("[AADWIK RIGIFY] ERROR: Rigify generation failed.")
    print("[AADWIK RIGIFY] The metarig checkpoint was saved for inspection.")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    raise RuntimeError("Rigify generation failed")

rig = bpy.context.object
if rig is None or rig.type != "ARMATURE":
    # Find likely generated rig.
    candidates = [o for o in bpy.data.objects if o.type == "ARMATURE" and o != metarig]
    if candidates:
        rig = candidates[-1]

if rig is None:
    raise RuntimeError("Rigify generated no armature.")

rig.name = "AADWIK_MAYA_RIGIFY_V1"
print("[AADWIK RIGIFY] Generated rig:", rig.name)

# -----------------------------
# Bind mesh using automatic weights
# -----------------------------
# Keep the metarig for regeneration/debugging, but don't bind it.
bpy.ops.object.select_all(action="DESELECT")
for obj in mesh_objects:
    if obj.type == "MESH":
        obj.select_set(True)

rig.select_set(True)
bpy.context.view_layer.objects.active = rig

try:
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    print("[AADWIK RIGIFY] Automatic skinning completed")
except Exception as e:
    print("[AADWIK RIGIFY] Automatic skinning failed:", repr(e))
    print("[AADWIK RIGIFY] Character mesh remains available for manual weighting.")

# -----------------------------
# Create a controlled test pose
# -----------------------------
bpy.context.view_layer.objects.active = rig
rig.select_set(True)

pose = rig.pose.bones

def rotate_if(name, x=0, y=0, z=0):
    b = pose.get(name)
    if not b:
        return False
    b.rotation_mode = "XYZ"
    b.rotation_euler = (x, y, z)
    return True

# Try common Rigify control names. These are controls, not DEF bones.
tests = [
    ("upper_arm_parent.L", 0.0, 0.0, math.radians(-20)),
    ("upper_arm_parent.R", 0.0, 0.0, math.radians(20)),
    ("hand.L", 0.0, 0.0, math.radians(-10)),
    ("hand.R", 0.0, 0.0, math.radians(10)),
    ("head", math.radians(-5), 0.0, math.radians(-8)),
]

applied = 0
for name, x, y, z in tests:
    if rotate_if(name, x, y, z):
        applied += 1

print(f"[AADWIK RIGIFY] Test pose controls applied: {applied}")

# -----------------------------
# Render a diagnostic image
# -----------------------------
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = int(get_arg("--width", "640"))
scene.render.resolution_y = int(get_arg("--height", "640"))
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = render_out

# Ensure character is visible and use a simple diagnostic camera.
cam = bpy.data.objects.get("AADWIK_RIGIFY_TEST_CAMERA")
if cam is None:
    cam_data = bpy.data.cameras.new("AADWIK_RIGIFY_TEST_CAMERA_DATA")
    cam = bpy.data.objects.new("AADWIK_RIGIFY_TEST_CAMERA", cam_data)
    bpy.context.collection.objects.link(cam)

cam.location = (0, -4.8, height * 0.52)
target = Vector((0, 0, height * 0.50))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 55
scene.camera = cam

# Ground
ground = bpy.data.objects.get("AADWIK_RIGIFY_TEST_GROUND")
if ground is None:
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0,0,0))
    ground = bpy.context.object
    ground.name = "AADWIK_RIGIFY_TEST_GROUND"

# Lights
for name, loc, energy, size in [
    ("AADWIK_KEY", (-3,-4,5), 900, 3),
    ("AADWIK_FILL", (3,-2,3), 500, 3),
    ("AADWIK_RIM", (0,3,4), 800, 2),
]:
    light = bpy.data.objects.get(name)
    if light is None:
        ld = bpy.data.lights.new(name, "AREA")
        light = bpy.data.objects.new(name, ld)
        bpy.context.collection.objects.link(light)
    light.location = loc
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    direction = Vector((0,0,height*0.5)) - light.location
    light.rotation_euler = direction.to_track_quat("-Z","Y").to_euler()

bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print("[AADWIK RIGIFY] BLEND SAVED:", blend_out)

bpy.ops.render.render(write_still=True)
print("[AADWIK RIGIFY] RENDER SAVED:", render_out)
print("[AADWIK RIGIFY] CHARACTER TEST COMPLETE")
