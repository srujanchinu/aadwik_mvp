import bpy
import json
import os
import math

SOURCE = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3.blend"
REPORT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\reports\aadwik_leg_deformation_comparison.json"

bpy.ops.wm.open_mainfile(filepath=SOURCE)

rig = bpy.data.objects.get("Aadwik_Main_Rig")
if rig is None:
    raise RuntimeError("Aadwik_Main_Rig not found")

pb = rig.pose.bones.get("foot_ik.L")
if pb is None:
    raise RuntimeError("foot_ik.L not found")

# Reset pose and record neutral evaluated geometry.
for p in rig.pose.bones:
    p.location = (0.0, 0.0, 0.0)
    p.rotation_euler = (0.0, 0.0, 0.0)
    p.scale = (1.0, 1.0, 1.0)

depsgraph = bpy.context.evaluated_depsgraph_get()

def evaluated_points(obj):
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    pts = [obj.matrix_world @ v.co for v in mesh.vertices]
    ev.to_mesh_clear()
    return pts

def stats(points):
    if not points:
        return {"vertices": 0}
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    zs = [p.z for p in points]
    return {
        "vertices": len(points),
        "bounds": {
            "x": [min(xs), max(xs)],
            "y": [min(ys), max(ys)],
            "z": [min(zs), max(zs)]
        },
        "center": [
            sum(xs) / len(xs),
            sum(ys) / len(ys),
            sum(zs) / len(zs)
        ]
    }

names = ["Human", "Human.bob01", "Human.female_sportsuit01", "Human.shoes05"]

neutral = {}
for name in names:
    obj = bpy.data.objects.get(name)
    if obj and obj.type == 'MESH':
        neutral[name] = stats(evaluated_points(obj))

# Apply the exact same controlled leg movement used in the earlier test.
pb.location.z = 0.09

# Update dependency graph so modifiers/constraints are evaluated.
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()

posed = {}
for name in names:
    obj = bpy.data.objects.get(name)
    if obj and obj.type == 'MESH':
        posed[name] = stats(evaluated_points(obj))

# Collect modifier visibility/type information, because Human contains
# hide/delete modifiers that can make raw mesh bounds misleading.
modifier_info = {}
for name in names:
    obj = bpy.data.objects.get(name)
    if not obj:
        continue
    modifier_info[name] = [
        {
            "name": m.name,
            "type": m.type,
            "show_viewport": bool(m.show_viewport),
            "show_render": bool(m.show_render),
            "object": m.object.name if hasattr(m, "object") and m.object else None
        }
        for m in obj.modifiers
    ]

report = {
    "source": SOURCE,
    "controller": "foot_ik.L",
    "test_z_offset_m": 0.09,
    "neutral_evaluated": neutral,
    "posed_evaluated": posed,
    "modifiers": modifier_info,
    "note": "Diagnostic only. No mesh, weights, rig, modifiers, or blend data were changed."
}

os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print("[OK] LEG DEFORMATION COMPARISON")
print(f"[OK] Report: {REPORT}")
print("[OK] Pose test: foot_ik.L Z = 0.09 m")
for name in names:
    if name in neutral and name in posed:
        print(f"[INFO] {name}: neutral={neutral[name]['vertices']} verts | posed={posed[name]['vertices']} verts")
print("[OK] No mesh, weights, rig, modifiers, or blend data were changed.")
