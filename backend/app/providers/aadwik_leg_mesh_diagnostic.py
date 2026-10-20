import bpy
import json

SOURCE = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3.blend"
REPORT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\reports\aadwik_leg_mesh_diagnostic.json"

bpy.ops.wm.open_mainfile(filepath=SOURCE)

names = ["Human", "Human.bob01", "Human.female_sportsuit01", "Human.shoes05"]
result = []

for name in names:
    obj = bpy.data.objects.get(name)
    if not obj or obj.type != 'MESH':
        result.append({"object": name, "found": False})
        continue

    verts_world = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not verts_world:
        result.append({"object": name, "found": True, "vertices": 0})
        continue

    xs = [v.x for v in verts_world]
    ys = [v.y for v in verts_world]
    zs = [v.z for v in verts_world]

    zmin, zmax = min(zs), max(zs)
    height = zmax - zmin

    # Report vertex distribution by vertical bands. This lets us identify
    # which mesh actually contains lower-leg/foot geometry without changing it.
    bands = {}
    for label, lo, hi in [
        ("bottom_20pct", zmin, zmin + height * 0.20),
        ("20_40pct", zmin + height * 0.20, zmin + height * 0.40),
        ("40_60pct", zmin + height * 0.40, zmin + height * 0.60),
        ("60_80pct", zmin + height * 0.60, zmin + height * 0.80),
        ("top_20pct", zmin + height * 0.80, zmax + 1e-9),
    ]:
        bands[label] = sum(lo <= z < hi for z in zs)

    result.append({
        "object": name,
        "found": True,
        "vertices": len(obj.data.vertices),
        "dimensions_world": [round(float(x), 5) for x in obj.dimensions],
        "world_bounds": {
            "x": [round(min(xs), 5), round(max(xs), 5)],
            "y": [round(min(ys), 5), round(max(ys), 5)],
            "z": [round(zmin, 5), round(zmax, 5)]
        },
        "vertical_vertex_distribution": bands,
        "armature_modifiers": [
            m.object.name if m.object else None
            for m in obj.modifiers if m.type == 'ARMATURE'
        ],
        "def_group_count": sum(
            1 for g in obj.vertex_groups if g.name.startswith("DEF-") or g.name.startswith("DEF_")
        )
    })

import os
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print("[OK] LEG MESH DIAGNOSTIC")
print(f"[OK] Report: {REPORT}")
for item in result:
    print(item)
print("[OK] No mesh, weights, rig, pose, or modifiers were changed.")
