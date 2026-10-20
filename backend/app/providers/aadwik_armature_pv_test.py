import bpy

SOURCE = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3.blend"
TEST = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3_no_armature_pv_test.blend"

bpy.ops.wm.open_mainfile(filepath=SOURCE)

rig = bpy.data.objects.get("Aadwik_Main_Rig")
body = bpy.data.objects.get("Human")
if not rig or not body:
    raise RuntimeError("Required rig/body not found")

pb = rig.pose.bones.get("foot_ik.L")
if not pb:
    raise RuntimeError("foot_ik.L not found")

# Reset pose.
for p in rig.pose.bones:
    p.location = (0,0,0)
    p.rotation_euler = (0,0,0)
    p.scale = (1,1,1)

# Disable ONLY the duplicate Armature PV modifier for this diagnostic.
pv = body.modifiers.get("Armature PV")
if not pv:
    raise RuntimeError("Armature PV modifier not found")
pv.show_viewport = False
pv.show_render = False

# Apply the same controlled IK movement.
pb.location.z = 0.09

# Pose mode, clean viewport.
if rig.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.overlay.show_overlays = False

bpy.ops.wm.save_as_mainfile(filepath=TEST)

print("[OK] ARMATURE PV A/B TEST")
print(f"[OK] Test file: {TEST}")
print("[OK] Armature PV: DISABLED for diagnostic only")
print("[OK] foot_ik.L Z offset: 0.09 m")
print("[OK] Original v3 master was not overwritten")
