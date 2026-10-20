import bpy

mat = bpy.data.materials.get("Human.high-poly")
if mat and mat.use_nodes:
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            image = node.image
            print("TEXTURE NODE:", node.name)
            print("IMAGE:", image.name if image else "None")
            print("PATH:", image.filepath if image else "None")
            print("SIZE:", tuple(image.size) if image else "None")
