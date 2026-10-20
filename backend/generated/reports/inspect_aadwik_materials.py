import bpy, json, os
from pathlib import Path

blend = r"generated\aadwik_character_master_v4_sportsuit_fix.blend"
out = r"generated\reports\aadwik_material_inspection.json"

bpy.ops.wm.open_mainfile(filepath=os.path.abspath(blend))

report = {"objects": []}
for obj in bpy.data.objects:
    if obj.type != "MESH" or obj.name.startswith("WGT-"):
        continue
    mats = []
    for slot in obj.material_slots:
        mat = slot.material
        if not mat:
            continue
        item = {"name": mat.name, "diffuse_color": list(mat.diffuse_color)}
        if mat.use_nodes and mat.node_tree:
            item["principled"] = []
            for node in mat.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    for key in ("Base Color", "Roughness", "Metallic", "Emission Color", "Emission Strength"):
                        socket = node.inputs.get(key)
                        if socket:
                            value = socket.default_value
                            item["principled"].append({
                                "input": key,
                                "value": list(value) if hasattr(value, "__len__") else value
                            })
        mats.append(item)
    if mats:
        report["objects"].append({"object": obj.name, "materials": mats})

Path(out).parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print("Material report saved:", os.path.abspath(out))
