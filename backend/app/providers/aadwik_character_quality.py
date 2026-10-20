
import bpy
import math
from mathutils import Vector

# ============================================================
# Aadwik Phase 23 - Visual Character Quality Upgrade
# Smooth cinematic-stylized characters.
# Public API intentionally preserved for the real movie route:
# build_tara, build_guardian, build_shadow, build_blue_star,
# apply_emotion, direct_character_gaze
# ============================================================

def _material(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission is not None:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    m.diffuse_color = (*color, 1.0)
    return m

def _smooth(obj):
    if obj and obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True

def _uv(name, loc, scale, material, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=rings, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    _smooth(o)
    return o

def _cube(name, loc, scale, material, bevel=0.15):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new("Rounded silhouette", "BEVEL")
        mod.width = bevel
        mod.segments = 4
    if material:
        o.data.materials.append(material)
    return o

def _cyl(name, loc, radius, depth, material, rotation=(0,0,0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth,
        location=loc, rotation=rotation
    )
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    _smooth(o)
    bevel = o.modifiers.new("Soft edges", "BEVEL")
    bevel.width = min(radius * 0.22, 0.08)
    bevel.segments = 3
    return o

def _parent(o, root):
    if o:
        o.parent = root

def _root(name, character_id, age=None):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root["character_id"] = character_id
    root["identity_locked"] = True
    root["visual_quality"] = "phase23_cinematic_smooth"
    if age is not None:
        root["age"] = age
    return root

def _face(root, head, skin, hair, eye_scale=(0.12,0.08,0.15)):
    # Front is -Y, so facial features sit toward negative Y.
    hx, hy, hz = head.location

    left_eye = _uv(
        "FACE_EYE_L", (hx-0.18, hy-0.39, hz+0.04),
        eye_scale, _material("MAT_EyeWhite", (0.97,0.98,1.0), roughness=0.18)
    )
    right_eye = _uv(
        "FACE_EYE_R", (hx+0.18, hy-0.39, hz+0.04),
        eye_scale, bpy.data.materials["MAT_EyeWhite"]
    )

    iris_mat = _material("MAT_Iris", (0.06,0.16,0.30), roughness=0.28)
    pupil_mat = _material("MAT_Pupil", (0.008,0.008,0.012), roughness=0.12)

    for side, x in (("L", hx-0.18), ("R", hx+0.18)):
        iris = _uv(
            f"FACE_IRIS_{side}", (x, hy-0.455, hz+0.04),
            (0.055,0.025,0.075), iris_mat, 24, 16
        )
        pupil = _uv(
            f"FACE_PUPIL_{side}", (x, hy-0.478, hz+0.04),
            (0.026,0.012,0.038), pupil_mat, 24, 16
        )
        _parent(iris, root); _parent(pupil, root)

    # Soft brows give the face readable acting without a mouth texture.
    brow_mat = hair
    for side, x in (("L", hx-0.18), ("R", hx+0.18)):
        brow = _cyl(
            f"FACE_BROW_{side}", (x, hy-0.445, hz+0.23),
            0.025, 0.16, brow_mat,
            rotation=(0, math.radians(90), math.radians(-8 if side=="L" else 8)),
            vertices=20
        )
        _parent(brow, root)

    # Small nose and friendly mouth.
    nose = _uv(
        "FACE_NOSE", (hx, hy-0.405, hz-0.06),
        (0.045,0.055,0.055), skin, 24, 16
    )
    mouth_mat = _material("MAT_Mouth", (0.32,0.06,0.08), roughness=0.5)
    mouth = _uv(
        "FACE_MOUTH", (hx, hy-0.435, hz-0.17),
        (0.075,0.025,0.025), mouth_mat, 24, 16
    )
    _parent(nose, root); _parent(mouth, root)

    for o in (left_eye, right_eye):
        _parent(o, root)

def build_tara():
    skin = _material("MAT_TaraSkin", (0.72,0.43,0.27), roughness=0.48)
    hair = _material("MAT_TaraHair", (0.12,0.055,0.025), roughness=0.42)
    dress = _material("MAT_TaraDress", (0.07,0.22,0.55), roughness=0.52)
    shirt = _material("MAT_TaraShirt", (0.90,0.92,0.98), roughness=0.48)
    pants = _material("MAT_TaraPants", (0.045,0.09,0.22), roughness=0.62)
    shoes = _material("MAT_TaraShoes", (0.025,0.028,0.04), roughness=0.32)
    hairband = _material("MAT_TaraBand", (0.88,0.18,0.24), roughness=0.42)

    root = _root("CHAR_TARA_ROOT", "char_tara_v3", age=12)
    root["design"] = "cinematic_stylized_child"
    root["identity_lock"] = {
        "hair": "dark_brown_long",
        "outfit": "blue_dress_white_shirt",
        "age": 12,
        "silhouette": "child_proportions"
    }

    # Legs and shoes.
    for side, x in (("L",-0.17),("R",0.17)):
        leg = _cyl(f"TARA_LEG_{side}", (x,0,0.72), 0.11, 0.95, pants)
        shoe = _uv(f"TARA_SHOE_{side}", (x,-0.10,0.22), (0.16,0.27,0.09), shoes)
        _parent(leg, root); _parent(shoe, root)

    # Torso: rounded layered clothing instead of a block.
    torso = _uv("TARA_TORSO", (0,0,1.30), (0.48,0.30,0.58), dress)
    shirt_front = _uv("TARA_SHIRT_FRONT", (0,-0.27,1.50), (0.29,0.055,0.30), shirt)
    collar = _uv("TARA_COLLAR", (0,-0.30,1.70), (0.16,0.045,0.08), shirt)
    _parent(torso, root); _parent(shirt_front, root); _parent(collar, root)

    # Arms with rounded hands.
    for side, x in (("L",-0.51),("R",0.51)):
        arm = _cyl(
            f"TARA_ARM_{side}", (x,0,1.32), 0.105, 0.72, dress,
            rotation=(0, math.radians(90), 0)
        )
        hand = _uv(f"TARA_HAND_{side}", (x*1.08,-0.01,0.95), (0.12,0.12,0.14), skin)
        _parent(arm, root); _parent(hand, root)

    # Head + ears.
    head = _uv("TARA_HEAD", (0,-0.02,2.18), (0.49,0.42,0.52), skin)
    ear_l = _uv("TARA_EAR_L", (-0.47,-0.01,2.18), (0.10,0.07,0.14), skin)
    ear_r = _uv("TARA_EAR_R", (0.47,-0.01,2.18), (0.10,0.07,0.14), skin)
    _parent(head, root); _parent(ear_l, root); _parent(ear_r, root)

    # Hair cap + bangs + side locks.
    cap = _uv("TARA_HAIR_CAP", (0,0.01,2.48), (0.51,0.43,0.31), hair)
    bangs = _uv("TARA_HAIR_BANGS", (0,-0.36,2.38), (0.39,0.09,0.25), hair)
    _parent(cap, root); _parent(bangs, root)

    for side, x in (("L",-0.43),("R",0.43)):
        lock = _cyl(
            f"TARA_HAIR_LOCK_{side}", (x,0.02,2.10),
            0.10, 0.70, hair
        )
        _parent(lock, root)

    band = _uv("TARA_HAIRBAND", (0,-0.06,2.49), (0.54,0.45,0.045), hairband)
    _parent(band, root)

    _face(root, head, skin, hair)

    # Small pendant adds identity.
    pendant_mat = _material("MAT_TaraPendant", (0.95,0.68,0.12), metallic=0.65, roughness=0.25)
    pendant = _uv("TARA_PENDANT", (0,-0.35,1.58), (0.055,0.025,0.07), pendant_mat, 24, 16)
    _parent(pendant, root)

    return root

def build_guardian():
    skin = _material("MAT_GuardianSkin", (0.38,0.62,0.88), roughness=0.4)
    body = _material("MAT_GuardianBody", (0.18,0.34,0.62), roughness=0.45)
    wing = _material("MAT_GuardianWing", (0.45,0.72,1.0), roughness=0.3, emission=(0.10,0.25,0.8), emission_strength=1.2)
    eye = _material("MAT_GuardianEye", (0.75,0.95,1.0), roughness=0.18, emission=(0.25,0.7,1.0), emission_strength=2.5)

    root = _root("CHAR_GUARDIAN_ROOT", "char_guardian_v3", age=1)
    root["identity_lock"] = {"species":"tiny_starlight_guardian","wings":True,"blue_glow":True}

    torso = _uv("GUARDIAN_TORSO", (0,0,0.78), (0.30,0.23,0.38), body)
    head = _uv("GUARDIAN_HEAD", (0,-0.01,1.30), (0.32,0.29,0.30), skin)
    _parent(torso, root); _parent(head, root)

    for side, x in (("L",-0.30),("R",0.30)):
        arm = _cyl(
            f"GUARDIAN_ARM_{side}", (x*0.72,0,0.83),
            0.065, 0.42, skin,
            rotation=(0,math.radians(90),0)
        )
        _parent(arm, root)

    for side, x in (("L",-0.12),("R",0.12)):
        foot = _uv(f"GUARDIAN_FOOT_{side}", (x,-0.04,0.34), (0.10,0.16,0.07), body)
        _parent(foot, root)

    # Oversized expressive eyes.
    for side, x in (("L",-0.115),("R",0.115)):
        e = _uv(f"GUARDIAN_EYE_{side}", (x,-0.275,1.33), (0.10,0.045,0.12), eye, 28, 18)
        _parent(e, root)

    # Wings.
    for side, x in (("L",-0.36),("R",0.36)):
        w = _uv(f"GUARDIAN_WING_{side}", (x,0.05,1.02), (0.34,0.09,0.48), wing)
        w.rotation_euler.y = math.radians(18 if side=="L" else -18)
        _parent(w, root)

    return root

def build_shadow():
    skin = _material("MAT_ShadowBody", (0.025,0.018,0.045), roughness=0.6)
    eye = _material("MAT_ShadowEye", (0.7,0.08,0.12), roughness=0.2, emission=(0.8,0.02,0.02), emission_strength=2.5)

    root = _root("CHAR_SHADOW_ROOT", "char_shadow_creature_v3")
    root["identity_lock"] = {"silhouette":"mysterious_soft_creature","eyes":"red_glow"}

    body = _uv("SHADOW_BODY", (0,0,1.15), (0.62,0.42,0.90), skin)
    head = _uv("SHADOW_HEAD", (0,-0.02,2.02), (0.56,0.42,0.52), skin)
    _parent(body, root); _parent(head, root)

    for side, x in (("L",-0.20),("R",0.20)):
        e = _uv(f"SHADOW_EYE_{side}", (x,-0.40,2.06), (0.09,0.035,0.13), eye, 24, 16)
        _parent(e, root)

    for side, x in (("L",-0.55),("R",0.55)):
        arm = _cyl(
            f"SHADOW_ARM_{side}", (x,0,1.25), 0.13, 1.05, skin,
            rotation=(0,math.radians(90),0)
        )
        _parent(arm, root)

    return root

def build_blue_star():
    root = _root("PROP_BLUE_STAR", "prop_blue_star_v3")
    root["identity_lock"] = {"color":"blue","glowing":True,"story_role":"guiding_star"}

    star_mat = _material(
        "MAT_BlueStar",
        (0.08,0.35,1.0),
        roughness=0.18,
        metallic=0.15,
        emission=(0.03,0.30,1.0),
        emission_strength=7.0
    )

    # Five-point stylized star assembled from overlapping elongated spheres.
    center = _uv("STAR_CENTER", (0,0,0), (0.22,0.10,0.22), star_mat)
    _parent(center, root)

    for i in range(5):
        a = math.radians(i*72.0 - 90.0)
        x = math.cos(a)*0.23
        z = math.sin(a)*0.23
        ray = _uv(
            f"STAR_RAY_{i}", (x,0,z),
            (0.09,0.055,0.30), star_mat, 24, 16
        )
        ray.rotation_euler.y = a
        _parent(ray, root)

    return root

def apply_emotion(root_name, emotion):
    root = bpy.data.objects.get(root_name)
    if not root:
        return

    e = str(emotion or "neutral").lower()

    # Use subtle whole-character posture changes rather than cartoon distortion.
    if "happy" in e or "joy" in e or "hope" in e:
        root.rotation_euler.x = math.radians(-3)
    elif "sad" in e or "fear" in e or "worried" in e:
        root.rotation_euler.x = math.radians(3)
    elif "surprise" in e or "wonder" in e or "discovery" in e:
        root.rotation_euler.x = math.radians(-1)
    else:
        root.rotation_euler.x = 0.0

def direct_character_gaze(root_name, target):
    root = bpy.data.objects.get(root_name)
    if not root:
        return

    target_vec = Vector(target)

    # Rotate only around Z so the character keeps grounded cinematic posture.
    direction = target_vec - root.matrix_world.translation
    if direction.length > 0.001:
        root.rotation_euler.z = math.atan2(-direction.x, -direction.y)
