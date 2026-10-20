# Aadwik Quick Knee Straighten v1.0
# Blender 5.2.x — run from Blender's Text Editor.
# Save a backup copy before running. The script only makes a tiny adjustment
# to configured IK pole controls; it never changes the rig structure/weights.
# If the result is worse, press Ctrl+Z immediately.

import bpy

RIG_NAME = "Aadwik_Main_Rig"
STEP = 0.03

rig = bpy.data.objects.get(RIG_NAME)
if not rig or rig.type != "ARMATURE":
    raise RuntimeError(f"Could not find armature: {RIG_NAME}")

changed = []
for side in ("L", "R"):
    mechanism = rig.pose.bones.get(f"MCH-shin_ik.{side}")
    if not mechanism:
        continue
    for c in mechanism.constraints:
        if c.type != "IK" or c.mute:
            continue
        pole_target = getattr(c, "pole_target", None)
        pole_name = getattr(c, "pole_subtarget", "")
        if pole_target == rig and pole_name:
            p = rig.pose.bones.get(pole_name)
            if p:
                before = tuple(p.location)
                p.location.x += STEP if side == "L" else -STEP
                changed.append((p.name, before, tuple(p.location)))

bpy.context.view_layer.update()
print("AADWIK QUICK KNEE CHECK")
if changed:
    for name, before, after in changed:
        print(name, "before:", before, "after:", after)
    print("Inspect both knees. If improved, save as a new version; otherwise press Ctrl+Z.")
else:
    print("No configured IK pole targets found. No changes made.")
    print("Do not move random bones; the actual pole control must be identified visually.")
