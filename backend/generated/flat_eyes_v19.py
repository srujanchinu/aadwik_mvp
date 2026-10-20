import bpy
from mathutils import Vector

out = bpy.path.abspath("//aadwik_v19_flat_eye_test.blend")
rig = bpy.data.objects.get("Aadwik_Main_Rig")
if not rig:
    raise RuntimeError("Aadwik_Main_Rig not found")

# Remove only the experimental eye details from this test copy.
for name in (
    "Aadwik_Iris_L", "Aadwik_Iris_R",
    "Aadwik_Pupil_L", "Aadwik_Pupil_R",
    "Aadwik_Eye_Highlight_L", "Aadwik_Eye_Highlight_R",
):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

def make_mat(name, color, roughness):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

iris_mat = make_mat("Aadwik_Flat_Iris_Brown", (0.16, 0.055, 0.018), 0.42)
pupil_mat = make_mat("Aadwik_Flat_Pupil", (0.006, 0.003, 0.002), 0.38)

def disk(name, location, radius_x, radius_z, depth, material):
    # A very flat UV sphere acts as a test overlay, not a full eyeball.
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32, ring_count=16, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = (radius_x, depth, radius_z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj

for side in ("L", "R"):
    bone = rig.data.bones.get("DEF-eye_iris." + side)
    if not bone:
        raise RuntimeError("Missing eye bone: " + side)

    center = rig.matrix_world @ bone.head_local
    x, y, z = center.x, center.y - 0.002, center.z

    disk("Aadwik_Iris_" + side, (x, y, z), 0.0048, 0.0048, 0.0006, iris_mat)
    disk("Aadwik_Pupil_" + side, (x, y - 0.0007, z), 0.0021, 0.0025, 0.00035, pupil_mat)

bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED:", out)
