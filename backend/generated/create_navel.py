import bpy
import math

obj = bpy.data.objects.get("Human")
if obj is None or obj.type != "MESH":
    raise RuntimeError("Human mesh not found")

# Work on the existing body mesh; no new .blend file is created.
if obj.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")

cx, cz = 0.0, 0.80
rx, rz = 0.014, 0.012
depth = 0.002

# Find vertices near the estimated front-abdomen area.
verts = obj.data.vertices
candidates = [
    v for v in verts
    if abs(v.co.x - cx) < rx
    and abs(v.co.z - cz) < rz
    and v.co.y < -0.07
]

if not candidates:
    print("No vertices matched. Mesh unchanged.")
else:
    # Save original coordinates in memory for this session.
    original = {v.index: v.co.copy() for v in candidates}
    moved = 0

    for v in candidates:
        dx = (v.co.x - cx) / rx
        dz = (v.co.z - cz) / rz
        r2 = dx * dx + dz * dz

        if r2 < 1.0:
            falloff = (1.0 - r2) ** 2
            v.co.y += depth * falloff
            moved += 1

    obj.data.update()
    print("Navel test applied to", moved, "vertices.")
    print("Inspect the abdomen before saving.")