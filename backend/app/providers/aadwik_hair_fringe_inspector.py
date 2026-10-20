# Aadwik Hair Fringe Inspector
# Diagnostic only. Does not modify or save the source .blend.
# Run from backend folder:
# blender.exe --background --python app\providers\aadwik_hair_fringe_inspector.py -- --source "generated\aadwik_character_master_v4_sportsuit_fix.blend" --report "generated\reports\aadwik_hair_fringe_inspection.json"

import bpy, sys, os, json

def arg_value(flag, default):
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    try:
        return args[args.index(flag) + 1]
    except (ValueError, IndexError):
        return default

source = os.path.abspath(arg_value("--source", "generated/aadwik_character_master_v4_sportsuit_fix.blend"))
report_path = os.path.abspath(arg_value("--report", "generated/reports/aadwik_hair_fringe_inspection.json"))
if not os.path.isfile(source):
    raise FileNotFoundError("Blend file not found: " + source)

bpy.ops.wm.open_mainfile(filepath=source)
hair = bpy.data.objects.get("Human.bob01")
body = bpy.data.objects.get("Human")
if hair is None or hair.type != "MESH":
    raise RuntimeError("Mesh object Human.bob01 was not found.")
if body is None or body.type != "MESH":
    raise RuntimeError("Body mesh Human was not found.")

mesh = hair.data
mins = [min(v.co[i] for v in mesh.vertices) for i in range(3)]
maxs = [max(v.co[i] for v in mesh.vertices) for i in range(3)]
edge_face_count = [0] * len(mesh.vertices)
for poly in mesh.polygons:
    for vi in poly.vertices:
        edge_face_count[vi] += 1
boundary = [
    {"index": v.index, "co": [round(float(c), 6) for c in v.co]}
    for v in mesh.vertices if edge_face_count[v.index] <= 2
]
report = {
    "source_blend": source,
    "hair_object": hair.name,
    "vertex_count": len(mesh.vertices),
    "polygon_count": len(mesh.polygons),
    "local_bounds": {"min": mins, "max": maxs, "dimensions": [maxs[i] - mins[i] for i in range(3)]},
    "world_location": [float(c) for c in hair.matrix_world.translation],
    "world_dimensions": [float(c) for c in hair.dimensions],
    "parent": hair.parent.name if hair.parent else None,
    "modifiers": [{"name": m.name, "type": m.type, "show_viewport": m.show_viewport, "show_render": m.show_render} for m in hair.modifiers],
    "body_object": body.name,
    "boundary_vertex_count": len(boundary),
    "boundary_vertex_sample_first_100": boundary[:100],
    "note": "Read-only inspection. No vertices, weights, modifiers, rig, or source file were changed."
}
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print("AADWIK_HAIR_FRINGE_INSPECTION_COMPLETE")
print("Hair:", hair.name)
print("Vertices:", len(mesh.vertices), "| Polygons:", len(mesh.polygons))
print("Local bounds:", report["local_bounds"])
print("Boundary vertices:", len(boundary))
print("Report saved:", report_path)
print("Source blend was not saved or modified.")
