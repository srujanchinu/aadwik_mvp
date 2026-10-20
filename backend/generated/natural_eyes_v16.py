import bpy

out = bpy.path.abspath("//aadwik_v16_natural_eyes.blend")

for side in ("L", "R"):
    iris = bpy.data.objects.get("Aadwik_Iris_" + side)
    pupil = bpy.data.objects.get("Aadwik_Pupil_" + side)

    # Recess the details slightly into the eye surface.
    for obj in (iris, pupil):
        if obj:
            obj.location.y += 0.0015

    # Keep the pupil dark but avoid an oversized, glossy appearance.
    if pupil:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Roughness"].default_value = 0.38
                    if "Coat Weight" in bsdf.inputs:
                        bsdf.inputs["Coat Weight"].default_value = 0.0

bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED:", out)
