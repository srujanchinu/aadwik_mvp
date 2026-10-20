import bpy, os, json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(r"generated\aadwik_character_master_v4_sportsuit_fix.blend"))
obj = bpy.data.objects.get("Human")
if not obj:
    print("ERROR: Human mesh not found")
else:
    result = {"object": obj.name, "materials": []}
    for slot in obj.material_slots:
        mat = slot.material
        if not mat:
            result["materials"].append(None)
            continue
        item = {"name": mat.name, "diffuse_color": list(mat.diffuse_color), "nodes": []}
        if mat.node_tree:
            for node in mat.node_tree.nodes:
                entry = {"type": node.type, "name": node.name}
                if node.type == "BSDF_PRINCIPLED":
                    socket = node.inputs.get("Base Color")
                    if socket:
                        entry["base_color"] = list(socket.default_value)
                elif node.type == "TEX_IMAGE":
                    entry["image"] = node.image.name if node.image else None
                item["nodes"].append(entry)
        result["materials"].append(item)
    print(json.dumps(result, indent=2))
