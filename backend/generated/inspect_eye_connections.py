import bpy

mat = bpy.data.materials.get("Human.high-poly")
if mat and mat.node_tree:
    for node in mat.node_tree.nodes:
        print("\nNODE:", node.name, node.type)
        for output in node.outputs:
            for link in output.links:
                print("  ->", link.to_node.name, "/", link.to_socket.name)
        if node.type == "TEX_IMAGE":
            print("  IMAGE:", node.image.name if node.image else "None")
    print("\nMATERIAL LINKS:")
    for link in mat.node_tree.links:
        print(link.from_node.name, "->", link.to_node.name,
              "|", link.from_socket.name, "->", link.to_socket.name)
