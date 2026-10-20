import bpy

o = bpy.data.objects["Human"]
print("MATERIALS:", [m.name for m in o.data.materials])

m = bpy.data.materials.get("Human.high-poly")
if m and m.use_nodes:
    print("NODES:", [(n.name, n.type) for n in m.node_tree.nodes])
else:
    print("NODES: disabled")

for name in ("Aadwik_Iris_L", "Aadwik_Pupil_L", "Aadwik_Iris_R", "Aadwik_Pupil_R"):
    obj = bpy.data.objects.get(name)
    if obj:
        print("EYE:", name, "dimensions:", tuple(round(v, 4) for v in obj.dimensions))
