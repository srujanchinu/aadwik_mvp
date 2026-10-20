# Aadwik Rigify IK Pole Switch Repair — Blender 5.2.x
# Repairs the pole-vector mute drivers on MCH-shin_ik.L and .R.
# Does not move bones, alter weights, or save automatically.
import bpy

rig = bpy.data.objects.get("Aadwik_Main_Rig")
if rig is None or rig.type != "ARMATURE":
    raise RuntimeError('Could not find armature "Aadwik_Main_Rig".')

for side in ("L", "R"):
    bone_name = f"MCH-shin_ik.{side}"
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        raise RuntimeError(f"Missing bone: {bone_name}")

    no_pole = next((c for c in pb.constraints if c.type == "IK" and c.name == "IK"), None)
    pole = next((c for c in pb.constraints if c.type == "IK" and c.name == "IK.001"), None)
    if no_pole is None or pole is None:
        raise RuntimeError(f"{bone_name} is missing IK / IK.001 constraints.")

    prop_path = f'pose.bones["thigh_parent.{side}"]["pole_vector"]'
    for con, expr in ((no_pole, "pv"), (pole, "not pv")):
        driver_path = f'pose.bones["{bone_name}"].constraints["{con.name}"].mute'
        try:
            rig.driver_remove(driver_path)
        except (TypeError, RuntimeError):
            pass
        fc = rig.driver_add(driver_path)
        d = fc.driver
        d.type = "SCRIPTED"
        while len(d.variables):
            d.variables.remove(d.variables[0])
        v = d.variables.new()
        v.name = "pv"
        v.type = "SINGLE_PROP"
        v.targets[0].id = rig
        v.targets[0].data_path = prop_path
        d.expression = expr

bpy.context.view_layer.update()
print("AADWIK IK POLE SWITCH REPAIR COMPLETE")
for side in ("L", "R"):
    prop = bool(rig.pose.bones[f"thigh_parent.{side}"].get("pole_vector", False))
    pb = rig.pose.bones[f"MCH-shin_ik.{side}"]
    print(side, "pole_vector =", prop,
          "| IK mute =", pb.constraints["IK"].mute,
          "| IK.001 mute =", pb.constraints["IK.001"].mute)
print("No bones, meshes, weights, or modifiers were changed.")
print("Inspect the character, then Save As to a NEW test file if the result is better.")
