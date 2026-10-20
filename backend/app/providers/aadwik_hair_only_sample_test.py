import bpy, math
from mathutils import Vector

# Aadwik HAIR-ONLY sample test
# Opens the existing character scene and adds ONLY hair.
# No clothing or body changes.

SRC = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_base_v1.blend"
OUT_BLEND = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_base_v1_HAIR_ONLY.blend"
OUT_PNG = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_base_v1_HAIR_ONLY.png"

# Load source
bpy.ops.wm.open_mainfile(filepath=SRC)

# Remove any previous test hair only
for obj in list(bpy.data.objects):
    if obj.name.startswith("AADWIK_TEST_HAIR"):
        bpy.data.objects.remove(obj, do_unlink=True)

# Find character and estimate head position from the visible human mesh.
human = bpy.data.objects.get("Human")
if human is None:
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    human = meshes[0] if meshes else None

if human is None:
    raise RuntimeError("Human mesh not found")

# World-space bounding box
corners = [human.matrix_world @ Vector(c) for c in human.bound_box]
min_z = min(v.z for v in corners)
max_z = max(v.z for v in corners)
height = max_z - min_z
center = sum(corners, Vector()) / 8.0

# Head is approximately the upper 15% of the character.
head_z = min_z + height * 0.91
head_center = Vector((center.x, center.y, head_z))

# Approximate head radius from overall height.
rx = height * 0.055
ry = height * 0.050
rz = height * 0.060

# Hair material
mat = bpy.data.materials.get("AADWIK_TEST_HAIR_MAT") or bpy.data.materials.new("AADWIK_TEST_HAIR_MAT")
mat.diffuse_color = (0.035, 0.012, 0.006, 1.0)
mat.roughness = 0.48

# Hemisphere hair cap
verts = []
faces = []
rings = 8
segments = 48

for r in range(rings + 1):
    phi = (math.pi / 2.0) * (r / rings)  # top -> equator
    z = math.cos(phi) * rz
    radial = math.sin(phi)
    for s in range(segments):
        a = 2.0 * math.pi * s / segments
        verts.append((
            head_center.x + rx * radial * math.cos(a),
            head_center.y + ry * radial * math.sin(a),
            head_center.z + z
        ))

for r in range(rings):
    for s in range(segments):
        a = r * segments + s
        b = r * segments + (s + 1) % segments
        c = (r + 1) * segments + (s + 1) % segments
        d = (r + 1) * segments + s
        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new("AADWIK_TEST_HAIR_CAP_MESH")
mesh.from_pydata(verts, [], faces)
mesh.update()

cap = bpy.data.objects.new("AADWIK_TEST_HAIR_CAP", mesh)
bpy.context.collection.objects.link(cap)
cap.data.materials.append(mat)

# Slightly larger than head so it sits on top rather than cutting into it.
cap.scale = (1.08, 1.08, 1.10)

bev = cap.modifiers.new("Hair Cap Smooth", "BEVEL")
bev.width = height * 0.004
bev.segments = 2

# Hair locks as smooth curves down the sides/back.
def hair_lock(name, points, radius):
    curve = bpy.data.curves.new(name + "_CURVE", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 4
    curve.bevel_depth = radius
    curve.bevel_resolution = 4
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bp, p in zip(spline.bezier_points, points):
        bp.co = p
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

# Side locks and longer back locks.
lock_r = height * 0.010
for side in (-1, 1):
    x = head_center.x + side * rx * 0.78
    hair_lock(
        f"AADWIK_TEST_HAIR_SIDE_{side}",
        [
            (x, head_center.y - ry*0.05, head_center.z + rz*0.48),
            (x + side*rx*0.08, head_center.y - ry*0.08, head_center.z + rz*0.05),
            (x + side*rx*0.05, head_center.y - ry*0.02, head_center.z - rz*0.55),
        ],
        lock_r
    )

for i in range(5):
    a = -0.55 + i * 0.275
    x = head_center.x + rx * math.sin(a) * 0.92
    y = head_center.y + ry * 0.82
    hair_lock(
        f"AADWIK_TEST_HAIR_BACK_{i}",
        [
            (x, y, head_center.z + rz*0.42),
            (x, y + ry*0.08, head_center.z),
            (x*0.0 + x, y + ry*0.12, head_center.z - rz*0.95),
        ],
        lock_r * 1.15
    )

# Camera: frame the character automatically.
scene = bpy.context.scene
cam = scene.camera
if cam is None:
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam

target = Vector((center.x, center.y, min_z + height*0.52))
cam.location = Vector((center.x + height*1.65, center.y - height*2.55, min_z + height*0.72))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 58

# Simple neutral lighting for the test.
world = scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.025,0.025,0.025,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

# Render
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = OUT_PNG

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
bpy.ops.render.render(write_still=True)

print("[AADWIK HAIR ONLY] COMPLETE")
print("[AADWIK HAIR ONLY] BLEND:", OUT_BLEND)
print("[AADWIK HAIR ONLY] PREVIEW:", OUT_PNG)
