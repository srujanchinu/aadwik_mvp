import bpy

for side in ("L", "R"):
    obj = bpy.data.objects.get("Aadwik_Eye_Highlight_" + side)
    if obj:
        obj.hide_render = True
        obj.hide_viewport = True

out = bpy.path.abspath("//aadwik_v12_eye_soft_test.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED:", out)
