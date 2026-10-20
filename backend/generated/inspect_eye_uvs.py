import bpy

for name in ("Human", "Human.high-poly"):
    obj = bpy.data.objects.get(name)
    if not obj or obj.type != "MESH":
        continue
    print("\nOBJECT:", name)
    print("UV MAPS:", [(uv.name, len(uv.data)) for uv in obj.data.uv_layers])
    print("VERTICES:", len(obj.data.vertices), "POLYGONS:", len(obj.data.polygons))
