import bpy, json, os

SOURCE = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3.blend"
REPORT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\reports\aadwik_body_leg_weights.json"

bpy.ops.wm.open_mainfile(filepath=SOURCE)

body = bpy.data.objects.get("Human")
rig = bpy.data.objects.get("Aadwik_Main_Rig")
if not body or not rig:
    raise RuntimeError("Human or Aadwik_Main_Rig not found")

# Analyze the lower-body vertices without changing anything.
# Use object-space Z because the body mesh is in its rest configuration.
zs = [v.co.z for v in body.data.vertices]
zmin, zmax = min(zs), max(zs)
height = zmax - zmin

# Focus on the lower ~55% of the body, then identify the strongest
# DEF influences. This is diagnostic only.
cutoff = zmin + height * 0.55
groups = {g.index: g.name for g in body.vertex_groups}

def is_def(name):
    return name.startswith("DEF-") or name.startswith("DEF_")

records = []
for v in body.data.vertices:
    if v.co.z > cutoff:
        continue

    influences = []
    for g in v.groups:
        name = groups.get(g.group)
        if name and is_def(name) and g.weight > 0:
            influences.append((name, float(g.weight)))

    influences.sort(key=lambda x: x[1], reverse=True)
    if influences:
        total = sum(w for _, w in influences)
        top = influences[:8]
        records.append({
            "vertex": v.index,
            "z": float(v.co.z),
            "top_influences": top,
            "def_weight_sum": total,
            "influence_count": len(influences)
        })

# Summarize the strongest DEF groups in the lower body.
summary = {}
for r in records:
    for name, weight in r["top_influences"]:
        s = summary.setdefault(name, {"vertices": 0, "weight_sum": 0.0, "max_weight": 0.0})
        s["vertices"] += 1
        s["weight_sum"] += weight
        s["max_weight"] = max(s["max_weight"], weight)

summary_list = []
for name, s in summary.items():
    summary_list.append({
        "bone": name,
        "vertices_in_top8": s["vertices"],
        "average_top_weight": s["weight_sum"] / s["vertices"],
        "max_weight": s["max_weight"]
    })
summary_list.sort(key=lambda x: x["vertices_in_top8"], reverse=True)

report = {
    "source": SOURCE,
    "body": "Human",
    "object_z_range": [zmin, zmax],
    "lower_body_cutoff_z": cutoff,
    "vertices_analyzed": len(records),
    "top_def_groups": summary_list[:30],
    "sample_vertices": sorted(records, key=lambda r: r["z"])[:100],
    "note": "Diagnostic only. No mesh, weights, rig, modifiers, or blend data were changed."
}

os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print("[OK] BODY LEG WEIGHT DIAGNOSTIC")
print(f"[OK] Report: {REPORT}")
print(f"[OK] Vertices analyzed: {len(records)}")
print("[OK] No mesh, weights, rig, modifiers, or blend data were changed.")
