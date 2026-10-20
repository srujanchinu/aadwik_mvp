import bpy

rig = bpy.data.objects.get("Aadwik_Main_Rig")
human = bpy.data.objects.get("Human")
if not rig or not human:
    raise RuntimeError("Expected rig or Human mesh is missing.")

print("RIG:", rig.name, "bones:", len(rig.data.bones))
print("HUMAN:", human.name, "vertices:", len(human.data.vertices))

for side in ("L", "R"):
    bone = rig.data.bones.get("DEF-eye_iris." + side)
    if bone:
        print("EYE BONE", side, "head:", tuple(round(v, 5) for v in bone.head_local))

for name in ("Human", "Human.high-poly"):
    obj = bpy.data.objects.get(name)
    if obj and obj.type == "MESH":
        print("MESH:", name, "UV maps:", [uv.name for uv in obj.data.uv_layers],
              "materials:", [m.name if m else None for m in obj.data.materials])

print("Inspection complete. No scene changes made.")
