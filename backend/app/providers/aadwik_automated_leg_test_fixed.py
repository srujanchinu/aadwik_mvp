import bpy

BLEND = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3.blend"
OUT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3_leg_test.blend"
RIG_NAME = "Aadwik_Main_Rig"
BONE_NAME = "foot_ik.L"
LIFT_Z = 0.09

# The blend is already supplied on Blender's command line, so just use
# the currently loaded scene. This avoids opening the file twice.
rig = bpy.data.objects.get(RIG_NAME)
if rig is None:
    raise RuntimeError(f"Rig not found: {RIG_NAME}")

pb = rig.pose.bones.get(BONE_NAME)
if pb is None:
    raise RuntimeError(f"Pose bone not found: {BONE_NAME}")

# Temporary automated deformation test.
# Move only the existing IK controller; no bones, constraints, or rig setup
# are created/changed.
pb.location = (0.0, 0.0, LIFT_Z)

# Make the rig active. Selection is optional for the test and is intentionally
# omitted to avoid Blender-version-specific Bone selection API issues.
bpy.context.view_layer.objects.active = rig
rig.select_set(True)

bpy.ops.wm.save_as_mainfile(filepath=OUT)

print("[OK] Automated leg test created:")
print(OUT)
print(f"[OK] Controller: {RIG_NAME} / {BONE_NAME}")
print(f"[OK] Temporary Z offset: {LIFT_Z} m")
print("[OK] Original v3 was not overwritten.")
