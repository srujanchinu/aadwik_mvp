import bpy

SOURCE = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3.blend"
TEST = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3_clean_leg_test.blend"

bpy.ops.wm.open_mainfile(filepath=SOURCE)

rig = bpy.data.objects.get("Aadwik_Main_Rig")
if rig is None:
    raise RuntimeError("Aadwik_Main_Rig not found")

bone_name = "foot_ik.L"
pb = rig.pose.bones.get(bone_name)
if pb is None:
    raise RuntimeError(f"{bone_name} not found")

# Reset pose transforms.
for p in rig.pose.bones:
    p.location = (0.0, 0.0, 0.0)
    p.rotation_euler = (0.0, 0.0, 0.0)
    p.scale = (1.0, 1.0, 1.0)

# Select the rig and enter Pose Mode.
if rig.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')

# Automated deformation test on the existing IK controller.
# No bone selection API is used because Blender 5.2 does not expose
# Bone.select in this context.
pb.location.z = 0.09

# Hide viewport overlays, including Rigify controller shapes.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.overlay.show_overlays = False

# Save diagnostic copy only. The v3 master is untouched.
bpy.ops.wm.save_as_mainfile(filepath=TEST)

print("[OK] CLEAN AUTOMATED LEG TEST")
print(f"[OK] Test file: {TEST}")
print(f"[OK] Rig mode: {rig.mode}")
print(f"[OK] Controller transform: {bone_name} Z=0.09 m")
print("[OK] Rigify overlays hidden")
print("[OK] v3 master was not overwritten")
