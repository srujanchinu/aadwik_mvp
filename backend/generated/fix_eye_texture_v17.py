import bpy

out = bpy.path.abspath("//aadwik_v17_eye_texture_fix.blend")

eye_mesh = bpy.data.objects.get("Human.high-poly")
if not eye_mesh or eye_mesh.type != "MESH":
    raise RuntimeError("Human.high-poly mesh not found; nothing changed.")

source_mat = bpy.data.materials.get("Human.high-poly")
if not source_mat or not source_mat.node_tree:
    raise RuntimeError("Original eye material not found; nothing changed.")

eye_mat = source_mat.copy()
eye_mat.name = "Aadwik_Natural_Eye_Texture"
eye_mesh.data.materials.clear()
eye_mesh.data.materials.append(eye_mat)

nodes = eye_mat.node_tree.nodes
links = eye_mat.node_tree.links
image = bpy.data.images.get("brown_eye.png")
if image is None:
    raise RuntimeError("brown_eye.png not found; nothing changed.")

bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
output = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
if not bsdf or not output:
    raise RuntimeError("Eye shader nodes missing; nothing changed.")

tex = next((n for n in nodes if n.type == "TEX_IMAGE"), None)
if tex is None:
    tex = nodes.new("ShaderNodeTexImage")
tex.image = image
tex.interpolation = "Linear"

links.clear()
links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
bsdf.inputs["Roughness"].default_value = 0.38
bsdf.inputs["Alpha"].default_value = 1.0

# Remove only the extra eye-detail objects created in our tests.
for name in (
    "Aadwik_Iris_L", "Aadwik_Iris_R",
    "Aadwik_Pupil_L", "Aadwik_Pupil_R",
    "Aadwik_Eye_Highlight_L", "Aadwik_Eye_Highlight_R",
):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED:", out)
print("Eye mesh now has its own material; Human skin material was not edited.")
