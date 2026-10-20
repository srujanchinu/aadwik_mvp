import bpy
import os

# Aadwik direct sportsuit fix
# The .blend is already loaded by Blender's -b command.
# No open_mainfile() call is used.

OUT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v4_sportsuit_fix.blend"
CLOTH_NAME = "Human.female_sportsuit01"

cloth = bpy.data.objects.get(CLOTH_NAME)
if cloth is None:
    raise RuntimeError("Human.female_sportsuit01 not found.")

mods = cloth.modifiers

arm = next((m for m in mods if m.type == 'ARMATURE'), None)
sub = next((m for m in mods if m.type == 'SUBSURF'), None)

if arm is None:
    raise RuntimeError("Sportsuit Armature modifier not found.")
if sub is None:
    raise RuntimeError("Sportsuit Subdivision modifier not found.")

# Put Armature deformation BEFORE Subdivision.
# This is the controlled fix; no bones, weights, geometry, masks, or widgets
# are modified.
arm_index = list(mods).index(arm)
sub_index = list(mods).index(sub)

if arm_index > sub_index:
    while list(mods).index(arm) > list(mods).index(sub):
        bpy.context.view_layer.objects.active = cloth
        cloth.select_set(True)
        bpy.ops.object.modifier_move_up(modifier=arm.name)
        cloth.select_set(False)

result_order = [
    {"name": m.name, "type": m.type}
    for m in cloth.modifiers
]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT)

print("AADWIK DIRECT SPORTSUIT FIX COMPLETE")
print("Sportsuit modifier order:")
for item in result_order:
    print("  - {} [{}]".format(item["name"], item["type"]))
print("Saved:", OUT)
