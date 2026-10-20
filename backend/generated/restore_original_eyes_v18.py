import bpy

for name in (
    "Aadwik_Iris_L", "Aadwik_Iris_R",
    "Aadwik_Pupil_L", "Aadwik_Pupil_R",
    "Aadwik_Eye_Highlight_L", "Aadwik_Eye_Highlight_R",
):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)
        print("Removed test object:", name)

out = bpy.path.abspath("//aadwik_v18_original_eyes.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED:", out)
