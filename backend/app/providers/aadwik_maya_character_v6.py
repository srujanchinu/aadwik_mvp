import bpy
import math
from mathutils import Vector
from pathlib import Path

print("[AADWIK MAYA V6] START - HUMAN SILHOUETTE")

OUT = Path(r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated")
OUT.mkdir(parents=True, exist_ok=True)
BLEND = OUT / "aadwik_maya_v6.blend"
PREVIEW = OUT / "maya_v6_preview.png"

# ---------- CLEAN ----------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.metaballs, bpy.data.meshes, bpy.data.curves,
                   bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    pass

# ---------- MATERIAL ----------
def mat(name, color, metallic=0.0, rough=0.45):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value = (*color, 1.0)
        bs.inputs["Roughness"].default_value = rough
        bs.inputs["Metallic"].default_value = metallic
    return m

skin = mat("MAYA_V6_SKIN", (0.72, 0.39, 0.23), rough=0.5)
hair = mat("MAYA_V6_HAIR", (0.035, 0.018, 0.012), rough=0.6)
dress = mat("MAYA_V6_DRESS", (0.10, 0.28, 0.62), rough=0.5)
scarf = mat("MAYA_V6_SCARF", (0.08, 0.72, 0.88), rough=0.4)
shoe = mat("MAYA_V6_SHOES", (0.055, 0.07, 0.10), rough=0.42)
white = mat("MAYA_V6_EYES", (0.97, 0.97, 0.97), rough=0.25)
iris = mat("MAYA_V6_IRIS", (0.10, 0.35, 0.55), rough=0.25)
pupil = mat("MAYA_V6_PUPIL", (0.01, 0.01, 0.01), rough=0.2)
ground_mat = mat("MAYA_V6_GROUND", (0.035, 0.05, 0.07), rough=0.7)

# ---------- HELPERS ----------
def uv(name, loc, scale, material, seg=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=seg, ring_count=rings, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def cyl_between(name, a, b, radius, material, verts=32):
    a, b = Vector(a), Vector(b)
    d = b-a
    mid = (a+b)/2
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=d.length, location=mid)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = d.to_track_quat('Z','Y')
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

# ---------- V6 BODY ----------
# Deliberately human-proportioned, with readable shoulder/waist/hip/limb landmarks.
# Body remains one connected metaball field; face/clothes/accessories are separate.
mb = bpy.data.metaballs.new("MAYA_V6_CONNECTED_BODY")
mb.resolution = 0.045
mb.render_resolution = 0.03
mb.threshold = 0.58
body = bpy.data.objects.new("MAYA_V6_CONNECTED_BODY", mb)
bpy.context.collection.objects.link(body)

def blob(co, radius):
    e = mb.elements.new()
    e.co = co
    e.radius = radius
    return e

# height about 5.0m; proportions intentionally child-like.
# torso
blob((0, 0, 2.75), 0.72)
blob((0, 0, 3.35), 0.66)
blob((0, 0, 2.25), 0.62)
# pelvis
blob((0, 0, 1.78), 0.68)
blob((0, 0, 1.48), 0.58)

# shoulders + arms
for side in (-1, 1):
    s = float(side)
    blob((0.62*s, 0, 3.25), 0.40)
    blob((0.92*s, 0, 2.92), 0.30)
    blob((1.12*s, 0, 2.48), 0.26)
    blob((1.15*s, 0, 2.15), 0.22)  # hand connection

# legs, with narrower joints and readable separation
for side in (-1, 1):
    s = float(side)
    blob((0.34*s, 0, 1.10), 0.40)
    blob((0.36*s, 0, 0.72), 0.31)
    blob((0.36*s, 0, 0.28), 0.27)

bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.convert(target='MESH')
body = bpy.context.object
body.name = "MAYA_V6_BODY_MESH"
body.data.materials.append(skin)

bev = body.modifiers.new("V6_SMOOTH", 'BEVEL')
bev.width = 0.045
bev.segments = 3
sub = body.modifiers.new("V6_SUBDIVISION", 'SUBSURF')
sub.levels = 1
sub.render_levels = 1
bpy.context.view_layer.objects.active = body
bpy.ops.object.shade_smooth()

# ---------- HEAD ----------
head = uv("MAYA_V6_HEAD", (0, -0.015, 4.48), (0.64, 0.57, 0.70), skin)
neck = uv("MAYA_V6_NECK", (0, 0, 3.91), (0.25, 0.23, 0.28), skin)

# ears
for s in (-1,1):
    uv(f"MAYA_V6_EAR_{s}", (0.59*s, -0.01, 4.48), (0.13,0.07,0.18), skin)

# ---------- FACE ----------
# Front is -Y.
for s in (-1,1):
    x = 0.235*s
    uv(f"MAYA_V6_EYE_{s}", (x,-0.515,4.58), (0.145,0.055,0.12), white, 32, 16)
    uv(f"MAYA_V6_IRIS_{s}", (x,-0.568,4.58), (0.065,0.022,0.070), iris, 24, 12)
    uv(f"MAYA_V6_PUPIL_{s}", (x,-0.585,4.58), (0.030,0.012,0.038), pupil, 20, 10)

# nose and mouth
uv("MAYA_V6_NOSE", (0,-0.55,4.36), (0.09,0.075,0.12), skin)
uv("MAYA_V6_MOUTH", (0,-0.555,4.17), (0.14,0.035,0.035), pupil)

# brows
for s in (-1,1):
    o = cyl_between(f"MAYA_V6_BROW_{s}",
                    (0.12*s,-0.56,4.78),(0.34*s,-0.55,4.80),
                    0.025, hair, 16)

# ---------- HAIR ----------
uv("MAYA_V6_HAIR_CAP", (0,0.03,4.88), (0.68,0.60,0.45), hair)
for s in (-1,1):
    for i in range(4):
        x = s*(0.42 + i*0.07)
        z = 4.63 - i*0.11
        uv(f"MAYA_V6_HAIR_LOCK_{s}_{i}", (x,-0.40,z),
           (0.10,0.10,0.24), hair, 24, 14)

# ---------- CLOTHING ----------
# Dress shell follows the readable torso silhouette.
uv("MAYA_V6_DRESS_BODICE", (0,0.02,2.72), (0.74,0.56,0.78), dress)
uv("MAYA_V6_DRESS_SKIRT", (0,0.03,1.95), (0.82,0.64,0.55), dress)
# scarf
cyl_between("MAYA_V6_SCARF_FRONT",(0,-0.48,3.45),(0,-0.50,2.85),0.11,scarf,24)

# shoes
for s in (-1,1):
    uv(f"MAYA_V6_SHOE_{s}", (0.36*s,-0.10,0.08), (0.34,0.48,0.16), shoe)
    uv(f"MAYA_V6_SOLE_{s}", (0.36*s,-0.13,-0.03), (0.37,0.51,0.07), pupil)

# hands
for s in (-1,1):
    uv(f"MAYA_V6_HAND_{s}", (1.15*s,-0.01,2.10), (0.22,0.18,0.25), skin)

# ---------- ROOT / METADATA ----------
root = bpy.data.objects.new("MAYA_V6_CHARACTER_ROOT", None)
bpy.context.collection.objects.link(root)
root["character_id"] = "char_maya_v6"
root["identity_locked"] = True
root["asset_version"] = "V6"
root["geometry_type"] = "connected_metaball_body_plus_face_clothing"
root["rig_ready"] = False
root["stage"] = "SINGLE_FRAME_GEOMETRY_GATE"

# ---------- GROUND ----------
bpy.ops.mesh.primitive_plane_add(size=14, location=(0,0,-0.10))
ground = bpy.context.object
ground.name = "MAYA_V6_GROUND"
ground.data.materials.append(ground_mat)

# ---------- CAMERA ----------
bpy.ops.object.camera_add(location=(0,-12.5,3.0))
cam = bpy.context.object
cam.name = "MAYA_V6_CAMERA"
bpy.context.scene.camera = cam
def look_at(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
look_at(cam,(0,0,2.45))
cam.data.lens = 58

# ---------- LIGHTING ----------
bpy.ops.object.light_add(type='AREA', location=(-4,-5,7))
key=bpy.context.object
key.name="V6_KEY"
key.data.energy=900
key.data.shape='DISK'
key.data.size=4.0
look_at(key,(0,0,2.6))

bpy.ops.object.light_add(type='AREA', location=(4,-3,4.5))
fill=bpy.context.object
fill.name="V6_FILL"
fill.data.energy=500
fill.data.size=3.0
look_at(fill,(0,0,2.6))

bpy.ops.object.light_add(type='AREA', location=(0,2.5,6))
rim=bpy.context.object
rim.name="V6_RIM"
rim.data.energy=700
rim.data.size=3.0
look_at(rim,(0,0,3.0))

# ---------- RENDER ----------
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=640
scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(PREVIEW)
scene.render.film_transparent=False

world=bpy.data.worlds.new("MAYA_V6_WORLD") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.012,0.018,0.03,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.35

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)

print("[AADWIK MAYA V6] SAVED:", BLEND)
print("[AADWIK MAYA V6] PREVIEW:", PREVIEW)
print("[AADWIK MAYA V6] COMPLETE")
