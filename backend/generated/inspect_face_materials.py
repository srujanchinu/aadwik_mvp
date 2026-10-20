import bpy
from collections import Counter

for name in ("Human", "Human.high-poly"):
    obj = bpy.data.objects.get(name)
    if not obj or obj.type != "MESH":
        continue

    print("\nOBJECT:", name)
    print("MATERIAL SLOTS:", [(i, m.name if m else None) for i, m in enumerate(obj.data.materials)])
    print("POLYGON MATERIAL COUNTS:", dict(Counter(p.material_index for p in obj.data.polygons)))
