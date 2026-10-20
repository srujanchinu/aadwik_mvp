import bpy
from mathutils import Matrix

out = bpy.path.abspath("//aadwik_v15_eye_refine.blend")

for side in ("L", "R"):
    iris = bpy.data.objects.get("Aadwik_Iris_" + side)
    pupil = bpy.data.objects.get("Aadwik_Pupil_" + side)
    highlight = bpy.data.objects.get("Aadwik_Eye_Highlight_" + side)

    if iris:
        iris.data.transform(Matrix.Scale(0.72, 4))
        iris.location.y += 0.002
    if pupil:
        pupil.data.transform(Matrix.Scale(0.75, 4))
        pupil.location.y += 0.002
    if highlight:
        bpy.data.objects.remove(highlight, do_unlink=True)

bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED:", out)
