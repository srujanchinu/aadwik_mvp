import bpy

for side in ("L", "R"):
    for prefix, factor in (
        ("Aadwik_Iris_", 0.78),
        ("Aadwik_Pupil_", 0.82),
        ("Aadwik_Eye_Highlight_", 0.75),
    ):
        obj = bpy.data.objects.get(prefix + side)
        if obj:
            obj.scale *= factor

out = bpy.path.abspath("//aadwik_v11_eye_refined.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED:", out)
