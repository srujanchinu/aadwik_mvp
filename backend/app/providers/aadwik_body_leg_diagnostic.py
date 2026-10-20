import bpy

SOURCE = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3.blend"
TEST = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3_body_leg_diagnostic.blend"

bpy.ops.wm.open_mainfile(filepath=SOURCE)

rig = bpy.data.objects.get("Aadwik_Main_Rig")
if rig is None:
    raise RuntimeError("Aadwik_Main_Rig not found")

pb = rig.pose.bones.get("foot_ik.L")
if pb is None:
    raise RuntimeError("foot_ik.L not found")

# Reset pose, then apply the same controlled leg movement.
for p in rig.pose.bones:
    p.location = (0.0, 0.0, 0.0)
    p.rotation_euler = (0.0, 0.0, 0.0)
    p.scale = (1.0, 1.0, 1.0)

pb.location.z = 0.09

# Temporarily hide clothing only, so we can determine whether the
# thigh/hip deformation comes from the body or from clothing weights.
clothing_names = [
    "Human.bob01",
    "Human.female_sportsuit01",
    "Human.shoes05",
]
for name in clothing_names:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_viewport = True
        obj.hide_render = True

# Pose Mode for the diagnostic, with overlays hidden for a clean view.
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

print("[OK] BODY-ONLY LEG DEFORMATION DIAGNOSTIC")
print(f"[OK] Test file: {TEST}")
print("[OK] Controller: foot_ik.L")
print("[OK] Z lift: 0.09 m")
print("[OK] Clothing hidden for diagnosis only")
print("[OK] v3 master was not overwritten")
