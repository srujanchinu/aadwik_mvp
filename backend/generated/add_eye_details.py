import bpy, math
from mathutils import Vector

src = bpy.data.filepath
out = bpy.path.abspath("//aadwik_v10_eye_detail_test.blend")

def mat(name, color, roughness):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = roughness
    return m

iris_mat = mat("Aadwik_Eye_Iris_Brown", (0.20, 0.075, 0.025), 0.28)
pupil_mat = mat("Aadwik_Eye_Pupil_Dark", (0.008, 0.004, 0.003), 0.18)
white_mat = mat("Aadwik_Eye_Catchlight", (1.0, 0.92, 0.78), 0.12)

# Eye bones give approximate centers; place details toward the front (-Y).
rig = bpy.data.objects.get("Aadwik_Main_Rig")
if not rig:
    raise RuntimeError("Aadwik_Main_Rig not found; no file saved.")

for side in ("L", "R"):
    bone = rig.data.bones.get("DEF-eye_iris." + side)
    if not bone:
        raise RuntimeError("Missing iris bone for " + side)
    center = rig.matrix_world @ bone.head_local
    x, y, z = center.x, center.y - 0.012, center.z

    def sphere(name, loc, scale, material):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=loc)
        obj = bpy.context.object
        obj.name = name
        obj.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obj.data.materials.append(material)
        for poly in obj.data.polygons:
            poly.use_smooth = True
        return obj

    sphere("Aadwik_Iris_" + side, (x, y, z), (0.008, 0.003, 0.008), iris_mat)
    sphere("Aadwik_Pupil_" + side, (x, y - 0.0025, z), (0.0038, 0.0018, 0.0045), pupil_mat)
    sphere("Aadwik_Eye_Highlight_" + side, (x - 0.002, y - 0.004, z + 0.0025), (0.0015, 0.001, 0.0015), white_mat)

bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED EYE TEST:", out)
