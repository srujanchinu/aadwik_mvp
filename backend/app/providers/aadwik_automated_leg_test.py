import bpy
import os

BLEND = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3.blend"
OUT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3_leg_test.blend"
RIG_NAME = "Aadwik_Main_Rig"
BONE_NAME = "foot_ik.L"
LIFT_Z = 0.09

bpy.ops.wm.open_mainfile(filepath=BLEND)

rig = bpy.data.objects.get(RIG_NAME)
if rig is None:
    raise RuntimeError(f"Rig not found: {RIG_NAME}")

pb = rig.pose.bones.get(BONE_NAME)
if pb is None:
    raise RuntimeError(f"Pose bone not found: {BONE_NAME}")

# Clear any existing pose transform on this controller, then apply a small
# automated vertical lift. This is a temporary visual deformation test only.
pb.location = (0.0, 0.0, LIFT_Z)

# Make the rig active and the test bone selected for easy inspection.
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
for b in rig.data.bones:
    b.select = False
rig.data.bones.get(BONE_NAME).select = True
rig.data.bones.active = rig.data.bones.get(BONE_NAME)

bpy.ops.wm.save_as_mainfile(filepath=OUT)

print("[OK] Automated leg test created:")
print(OUT)
print(f"[OK] {RIG_NAME} / {BONE_NAME} Z offset = {LIFT_Z} m")
