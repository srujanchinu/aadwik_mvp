# Aadwik Rig Knee Inspector v1.0
# Blender 5.2.x — READ ONLY. Does not change pose, constraints, weights, or actions.
import bpy

RIG_NAME = "Aadwik_Main_Rig"
rig = bpy.data.objects.get(RIG_NAME)
if not rig or rig.type != "ARMATURE":
    raise RuntimeError(f"Armature not found: {RIG_NAME}")

print("\n========== AADWIK KNEE / IK-FK INSPECTION (READ ONLY) ==========")
print("Rig:", rig.name, "| rig_id:", rig.data.get("rig_id", "missing"))
print("Active action:", rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else "None")

for side in ("L", "R"):
    print(f"\n--- {side} LEG ---")
    for name in (f"thigh_fk.{side}", f"shin_fk.{side}", f"thigh_ik.{side}",
                 f"foot_ik.{side}", f"thigh_ik_target.{side}",
                 f"MCH-thigh_ik_target.{side}", f"MCH-shin_ik.{side}",
                 f"ORG-thigh.{side}", f"ORG-shin.{side}",
                 f"DEF-thigh.{side}", f"DEF-shin.{side}",
                 f"VIS_thigh_ik_pole.{side}"):
        p = rig.pose.bones.get(name)
        if not p:
            continue
        print("BONE", name,
              "| loc", tuple(round(float(v), 4) for v in p.location),
              "| rot", tuple(round(float(v), 4) for v in p.rotation_euler),
              "| parent", p.parent.name if p.parent else None)
        for c in p.constraints:
            details = [
                ("type", c.type),
                ("mute", c.mute),
                ("influence", round(float(c.influence), 4)),
            ]
            if hasattr(c, "subtarget"):
                details.append(("target", c.target.name if c.target else None))
                details.append(("subtarget", c.subtarget))
            if c.type == "IK":
                details.extend([
                    ("pole_target", c.pole_target.name if c.pole_target else None),
                    ("pole_subtarget", c.pole_subtarget),
                    ("chain_count", c.chain_count),
                    ("use_stretch", c.use_stretch),
                ])
            print("  CONSTRAINT", c.name, details)

# Report driver expressions and paths that mention leg controls or FK/IK.
print("\n--- RELEVANT DRIVERS ---")
ad = rig.animation_data
found = 0
if ad:
    for fc in ad.drivers:
        path = fc.data_path.lower()
        if any(k in path for k in ("ik", "fk", "thigh", "shin", "knee", "pole")):
            print("DRIVER", fc.data_path, "index", fc.array_index,
                  "expression", fc.driver.expression if fc.driver else None)
            for var in (fc.driver.variables if fc.driver else []):
                print("  VAR", var.name, var.type,
                      [(t.id.name if t.id else None, t.data_path) for t in var.targets])
            found += 1
print("Relevant driver count:", found)
print("\nInspection complete. READ ONLY — no changes made.")
