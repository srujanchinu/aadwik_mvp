import bpy
from mathutils import Matrix

src = bpy.data.filepath
out = bpy.path.abspath("//aadwik_v14_eye_parent_fix.blend")
rig = bpy.data.objects["Aadwik_Main_Rig"]

for side in ("L", "R"):
    bone_name = "DEF-eye_iris." + side
    bone = rig.data.bones[bone_name]
    target = rig.matrix_world @ bone.head_local
    x, y, z = target.x, target.y - 0.006, target.z

    for name, loc in (
        ("Aadwik_Iris_" + side, (x, y, z)),
        ("Aadwik_Pupil_" + side, (x, y - 0.0015, z)),
        ("Aadwik_Eye_Highlight_" + side, (x - 0.001, y - 0.0025, z + 0.0015)),
    ):
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue

        # Preserve the object's world transform while removing the faulty parent.
        world_matrix = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = world_matrix

        # Place the details near the eye bones without changing their size.
        obj.location = loc

bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED:", out)
