import bpy, json, os
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(r"generated\aadwik_character_master_v4_sportsuit_fix.blend"))
obj = bpy.data.objects.get("Human.bob01")
if not obj:
    print("ERROR: Human.bob01 not found")
else:
    print(json.dumps({
        "name": obj.name,
        "type": obj.type,
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
        "location": list(obj.location),
        "dimensions": list(obj.dimensions),
        "parent": obj.parent.name if obj.parent else None,
        "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers],
        "vertex_groups": [g.name for g in obj.vertex_groups]
    }, indent=2))
