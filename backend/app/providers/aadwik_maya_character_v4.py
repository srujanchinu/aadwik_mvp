import bpy
from mathutils import Vector
import math

# =========================================================
# AADWIK MAYA V4 — CHARACTER GEOMETRY FOUNDATION
# Single-frame quality gate. No movie pipeline changes.
# =========================================================

OUT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_v4.blend"

print("[AADWIK MAYA V4] START")
print("[AADWIK MAYA V4] CONNECTED BODY / HUMAN SILHOUETTE")

# ---------------------------------------------------------
# CLEAN SCENE
# ---------------------------------------------------------
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                   bpy.data.cameras, bpy.data.lights):
    for block in list(datablocks):
        try:
            datablocks.remove(block)
        except Exception:
            pass

# ---------------------------------------------------------
# MATERIALS
# ---------------------------------------------------------
def mat(name, color, roughness=.42, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m

skin = mat("MAYA_V4_Skin", (0.55, 0.25, 0.12), .38)
skin2 = mat("MAYA_V4_Skin_Light", (0.68, 0.34, 0.18), .40)
dress = mat("MAYA_V4_Dress", (0.035, 0.16, 0.55), .32)
scarf = mat("MAYA_V4_Scarf", (0.02, 0.62, 0.82), .30)
hair = mat("MAYA_V4_Hair", (0.018, 0.012, 0.010), .28)
shoe = mat("MAYA_V4_Shoes", (0.025, 0.035, 0.08), .24)
white = mat("MAYA_V4_EyeWhite", (0.92, 0.95, 1.0), .22)
iris = mat("MAYA_V4_Iris", (0.08, 0.42, 0.68), .20)
black = mat("MAYA_V4_Pupil", (0.004, 0.004, 0.006), .18)
mouth = mat("MAYA_V4_Mouth", (0.12, 0.012, 0.015), .35)

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def smooth(obj):
    if obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True

def uv(name, loc, scale, material, seg=64, rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=seg, ring_count=rings, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    smooth(o)
    return o

def capsule(name, a, b, r1, r2, material, seg=48):
    a = Vector(a); b = Vector(b)
    d = b - a
    length = d.length
    mid = (a + b) * .5

    bpy.ops.mesh.primitive_cone_add(
        vertices=seg,
        radius1=r1,
        radius2=r2,
        depth=length,
        location=mid
    )
    o = bpy.context.object
    o.name = name

    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    o.data.materials.append(material)
    smooth(o)
    return o

def ring_mesh(name, rings, material, segments=64):
    verts = []
    faces = []

    for z, rx, ry in rings:
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts.append((rx * math.cos(a), ry * math.sin(a), z))

    for r in range(len(rings)-1):
        for i in range(segments):
            a = r * segments + i
            b = r * segments + (i+1) % segments
            c = (r+1) * segments + (i+1) % segments
            d = (r+1) * segments + i
            faces.append((a,b,c,d))

    # caps
    bottom = len(verts)
    verts.append((0,0,rings[0][0]))
    top = len(verts)
    verts.append((0,0,rings[-1][0]))

    for i in range(segments):
        ni = (i+1) % segments
        faces.append((bottom, ni, i))
        a = (len(rings)-1)*segments+i
        b = (len(rings)-1)*segments+ni
        faces.append((top, a, b))

    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    smooth(o)
    return o

# ---------------------------------------------------------
# CONNECTED BODY FOUNDATION
# ---------------------------------------------------------
# Human-like torso: narrower waist, broader shoulders,
# distinct pelvis instead of one giant oval.
body_parts = []

body_parts.append(
    ring_mesh(
        "MAYA_V4_BODY",
        [
            (0.92, .27, .19),   # pelvis
            (1.10, .34, .23),
            (1.38, .31, .215), # waist
            (1.62, .39, .25),  # rib cage
            (1.88, .46, .27),  # shoulders
            (2.04, .20, .17),  # neck base
        ],
        skin
    )
)

# pelvis/leg junction volumes
body_parts += [
    uv("MAYA_V4_PELVIS_L", (-.17,0,.88), (.19,.18,.20), skin),
    uv("MAYA_V4_PELVIS_R", ( .17,0,.88), (.19,.18,.20), skin),
]

# legs: clear thigh -> knee -> shin proportions
body_parts += [
    capsule("MAYA_V4_THIGH_L", (-.17,0,.90), (-.17,0,.52), .145, .125, skin),
    capsule("MAYA_V4_SHIN_L", (-.17,0,.50), (-.17,0,.15), .115, .095, skin2),
    capsule("MAYA_V4_THIGH_R", (.17,0,.90), (.17,0,.52), .145, .125, skin),
    capsule("MAYA_V4_SHIN_R", (.17,0,.50), (.17,0,.15), .115, .095, skin2),
]

# feet
body_parts += [
    uv("MAYA_V4_FOOT_L", (-.17,-.055,.08), (.17,.27,.075), shoe),
    uv("MAYA_V4_FOOT_R", (.17,-.055,.08), (.17,.27,.075), shoe),
]

# arms with actual shoulder/upper-arm/elbow/forearm segmentation
body_parts += [
    uv("MAYA_V4_SHOULDER_L", (-.48,0,1.78), (.15,.14,.17), skin),
    uv("MAYA_V4_SHOULDER_R", (.48,0,1.78), (.15,.14,.17), skin),

    capsule("MAYA_V4_UPPER_ARM_L", (-.51,0,1.70), (-.59,0,1.34), .115, .095, skin),
    capsule("MAYA_V4_FOREARM_L", (-.59,0,1.31), (-.60,0,1.02), .092, .078, skin2),

    capsule("MAYA_V4_UPPER_ARM_R", (.51,0,1.70), (.59,0,1.34), .115, .095, skin),
    capsule("MAYA_V4_FOREARM_R", (.59,0,1.31), (.60,0,1.02), .092, .078, skin2),
]

# hands with actual palm and fingers
for side, x in (("L",-0.60), ("R",0.60)):
    body_parts.append(
        uv(f"MAYA_V4_HAND_{side}", (x,-.005,.94), (.095,.075,.105), skin2)
    )
    for i in range(5):
        fx = x + (-.065 + i*.032)
        body_parts.append(
            capsule(
                f"MAYA_V4_FINGER_{side}_{i}",
                (fx,-.055,.92),
                (fx,-.09,.84 + (0.018 if i==2 else 0)),
                .018,.012,skin2,24
            )
        )

# ---------------------------------------------------------
# HEAD / NECK
# ---------------------------------------------------------
uv("MAYA_V4_NECK", (0,0,2.10), (.16,.15,.16), skin)

# head is vertically shaped, not a simple ball
head = ring_mesh(
    "MAYA_V4_HEAD",
    [
        (2.12,.17,.15),
        (2.22,.28,.22),
        (2.45,.31,.245),
        (2.68,.27,.22),
        (2.78,.19,.16),
    ],
    skin,
    64
)

# subtle jaw/chin volume
uv("MAYA_V4_CHIN", (0,-.025,2.19), (.13,.12,.10), skin2)

# ---------------------------------------------------------
# EYES / FACE
# ---------------------------------------------------------
for side, x in (("L",-0.105),("R",0.105)):
    uv(f"MAYA_V4_EYE_{side}", (x,-.235,2.49), (.073,.035,.083), white, 48,24)
    uv(f"MAYA_V4_IRIS_{side}", (x,-.268,2.49), (.037,.012,.045), iris, 40,20)
    uv(f"MAYA_V4_PUPIL_{side}", (x,-.279,2.49), (.016,.008,.021), black, 32,16)

# brows
capsule("MAYA_V4_BROW_L", (-.18,-.258,2.60), (-.055,-.268,2.62), .018,.014,hair,24)
capsule("MAYA_V4_BROW_R", (.055,-.268,2.62), (.18,-.258,2.60), .014,.018,hair,24)

# nose
uv("MAYA_V4_NOSE", (0,-.27,2.39), (.045,.035,.07), skin2,40,20)

# mouth
capsule("MAYA_V4_MOUTH", (-.065,-.275,2.285), (.065,-.275,2.285), .014,.014,mouth,32)

# ears
uv("MAYA_V4_EAR_L", (-.285,0,2.43), (.045,.035,.09), skin2)
uv("MAYA_V4_EAR_R", (.285,0,2.43), (.045,.035,.09), skin2)

# ---------------------------------------------------------
# HAIR — layered curves/volumes, not one cap
# ---------------------------------------------------------
uv("MAYA_V4_HAIR_CROWN", (0,.015,2.73), (.30,.25,.14), hair)

for i, x in enumerate([-.27,-.20,-.13,-.06,.06,.13,.20,.27]):
    capsule(
        f"MAYA_V4_HAIR_LOCK_{i}",
        (x,.0,2.69),
        (x*1.04,.01,2.25 + .03*math.cos(i)),
        .038,.025,hair,32
    )

# side hair volumes
uv("MAYA_V4_HAIR_SIDE_L", (-.275,.015,2.47), (.065,.08,.30), hair)
uv("MAYA_V4_HAIR_SIDE_R", (.275,.015,2.47), (.065,.08,.30), hair)

# ---------------------------------------------------------
# CLOTHING
# ---------------------------------------------------------
dress_obj = ring_mesh(
    "MAYA_V4_DRESS",
    [
        (1.08,.34,.24),
        (1.30,.35,.25),
        (1.58,.43,.28),
        (1.83,.48,.29),
    ],
    dress
)

# scarf
capsule("MAYA_V4_SCARF_COLLAR", (-.13,-.03,2.08), (.13,-.03,2.08), .055,.055,scarf,40)
capsule("MAYA_V4_SCARF_TAIL", (.13,-.03,2.08), (.20,-.07,1.83), .05,.025,scarf,40)

# shoes/soles
uv("MAYA_V4_SOLE_L", (-.17,-.065,.035), (.18,.29,.035), shoe)
uv("MAYA_V4_SOLE_R", (.17,-.065,.035), (.18,.29,.035), shoe)

# ---------------------------------------------------------
# BODY METADATA
# ---------------------------------------------------------
root = bpy.data.objects.new("MAYA_V4_CHARACTER_ROOT", None)
bpy.context.collection.objects.link(root)

root["character_id"] = "char_maya_v4"
root["identity_locked"] = True
root["asset_version"] = "V4"
root["geometry_type"] = "human_stylized_3d"
root["rig_ready"] = False
root["quality_gate"] = "geometry_only"

# parent all character objects
for obj in list(bpy.context.scene.objects):
    if obj == root:
        continue
    if obj.type in {"MESH", "CURVE"}:
        obj.parent = root

# ---------------------------------------------------------
# GROUND / CAMERA
# ---------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=8, location=(0,0,0))
ground = bpy.context.object
ground.name = "MAYA_V4_GROUND"
ground.data.materials.append(mat("MAYA_V4_Ground", (.035,.045,.06), .72))

bpy.ops.object.camera_add(location=(0,-7.4,2.15))
cam = bpy.context.object
cam.name = "MAYA_V4_CAMERA"
bpy.context.scene.camera = cam

def point_camera(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z","Y").to_euler()

point_camera(cam, (0,0,1.42))
cam.data.lens = 58

# lighting
bpy.ops.object.light_add(type="AREA", location=(-3.2,-4.0,4.8))
key = bpy.context.object
key.name = "MAYA_V4_KEY"
key.data.energy = 900
key.data.shape = "DISK"
key.data.size = 3.0
point_camera(key, (0,0,1.5))

bpy.ops.object.light_add(type="AREA", location=(3.2,-2.0,3.2))
fill = bpy.context.object
fill.name = "MAYA_V4_FILL"
fill.data.energy = 550
fill.data.size = 2.5
point_camera(fill, (0,0,1.5))

bpy.ops.object.light_add(type="AREA", location=(0,2.5,4.0))
rim = bpy.context.object
rim.name = "MAYA_V4_RIM"
rim.data.energy = 800
rim.data.size = 2.0
point_camera(rim, (0,0,1.8))

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\maya_v4_preview.png"

scene.world.color = (.015,.02,.035)

bpy.ops.wm.save_as_mainfile(filepath=OUT)
bpy.ops.render.render(write_still=True)

print("[AADWIK MAYA V4] SAVED:", OUT)
print("[AADWIK MAYA V4] PREVIEW:", scene.render.filepath)
print("[AADWIK MAYA V4] COMPLETE")
