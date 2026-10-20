from __future__ import annotations

import bpy
import math
from mathutils import Vector


def material(name, color, roughness=0.55, metallic=0.0, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1.0)

    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 5.0
    return m


def add_uv(name, location, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32, ring_count=20, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def add_cube(name, location, scale, mat, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Character Soft Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 4
    obj.data.materials.append(mat)
    return obj


def add_cylinder(name, location, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def build_tara(location=(-1.4, 0, 0)):
    x, y, z = location
    root = bpy.data.objects.new("CHAR_TARA_ROOT", None)
    bpy.context.collection.objects.link(root)

    skin = material("TARA_SKIN", (0.70, 0.38, 0.23), roughness=0.72)
    hair = material("TARA_HAIR", (0.025, 0.012, 0.008), roughness=0.5)
    shirt = material("TARA_SHIRT", (0.10, 0.32, 0.78), roughness=0.7)
    skirt = material("TARA_SKIRT", (0.16, 0.08, 0.38), roughness=0.75)
    shoe = material("TARA_SHOES", (0.035, 0.035, 0.05), roughness=0.65)
    eye = material("TARA_EYES", (0.012, 0.008, 0.006), roughness=0.3)

    body = add_uv("TARA_BODY", (x, y, z + 1.15), (0.34, 0.23, 0.50), shirt)
    skirt_obj = add_uv("TARA_SKIRT", (x, y, z + 0.62), (0.43, 0.30, 0.34), skirt)
    head = add_uv("TARA_HEAD", (x, y, z + 2.02), (0.35, 0.31, 0.39), skin)
    hair_top = add_uv("TARA_HAIR_TOP", (x, y + 0.01, z + 2.32), (0.37, 0.33, 0.22), hair)

    # Hair side locks
    for side in (-1, 1):
        add_uv(
            f"TARA_HAIR_SIDE_{side}",
            (x + side * 0.29, y, z + 2.08),
            (0.11, 0.19, 0.32),
            hair,
        )

    # Eyes
    for side in (-1, 1):
        add_uv(
            f"TARA_EYE_{side}",
            (x + side * 0.115, y - 0.292, z + 2.05),
            (0.052, 0.028, 0.065),
            eye,
        )

    # Arms
    for side in (-1, 1):
        add_cylinder(
            f"TARA_ARM_{side}",
            (x + side * 0.42, y, z + 1.18),
            0.075,
            0.62,
            skin,
            (0, math.pi / 2, 0),
        )

    # Legs
    for side in (-1, 1):
        add_cylinder(
            f"TARA_LEG_{side}",
            (x + side * 0.14, y, z + 0.18),
            0.095,
            0.52,
            skin,
        )
        add_uv(
            f"TARA_SHOE_{side}",
            (x + side * 0.14, y - 0.10, z - 0.05),
            (0.15, 0.23, 0.08),
            shoe,
        )

    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith("TARA_"):
            obj.parent = root

    root["character_id"] = "char_tara_v2"
    root["identity_locked"] = True
    root["age"] = 12
    root["design"] = "cinematic_stylized_child"

    return root


def build_guardian(location=(1.0, 0, 1.0)):
    x, y, z = location
    root = bpy.data.objects.new("CHAR_GUARDIAN_ROOT", None)
    bpy.context.collection.objects.link(root)

    body_mat = material(
        "GUARDIAN_BODY", (0.18, 0.55, 0.86),
        roughness=0.38, emission=(0.02, 0.12, 0.45)
    )
    wing_mat = material(
        "GUARDIAN_WINGS", (0.22, 0.75, 1.0),
        roughness=0.3, emission=(0.04, 0.30, 0.80)
    )
    eye_mat = material(
        "GUARDIAN_EYES", (0.75, 0.95, 1.0),
        roughness=0.2, emission=(0.5, 0.8, 1.0)
    )

    body = add_uv("GUARDIAN_BODY", (x, y, z), (0.42, 0.30, 0.45), body_mat)
    head = add_uv("GUARDIAN_HEAD", (x, y - 0.02, z + 0.43), (0.34, 0.28, 0.30), body_mat)

    for side in (-1, 1):
        add_uv(
            f"GUARDIAN_EYE_{side}",
            (x + side * 0.12, y - 0.27, z + 0.47),
            (0.055, 0.025, 0.07),
            eye_mat,
        )
        add_uv(
            f"GUARDIAN_WING_{side}",
            (x + side * 0.48, y + 0.02, z + 0.12),
            (0.34, 0.08, 0.28),
            wing_mat,
        )

    root["character_id"] = "char_guardian_v2"
    root["identity_locked"] = True
    root["design"] = "magical_young_guardian"

    return root


def build_shadow(location=(1.5, 0, 0)):
    x, y, z = location
    root = bpy.data.objects.new("CHAR_SHADOW_ROOT", None)
    bpy.context.collection.objects.link(root)

    body_mat = material(
        "SHADOW_BODY", (0.018, 0.010, 0.035),
        roughness=0.48
    )
    eye_mat = material(
        "SHADOW_EYES", (0.9, 0.08, 0.03),
        roughness=0.25, emission=(0.8, 0.02, 0.01)
    )

    body = add_uv("SHADOW_BODY", (x, y, z + 1.15), (0.45, 0.32, 0.95), body_mat)
    head = add_uv("SHADOW_HEAD", (x, y, z + 2.15), (0.48, 0.34, 0.45), body_mat)

    for side in (-1, 1):
        add_uv(
            f"SHADOW_EYE_{side}",
            (x + side * 0.16, y - 0.31, z + 2.18),
            (0.075, 0.025, 0.055),
            eye_mat,
        )

    # Angular horns / silhouette accents
    for side in (-1, 1):
        add_cylinder(
            f"SHADOW_HORN_{side}",
            (x + side * 0.25, y, z + 2.55),
            0.08,
            0.42,
            body_mat,
            (0, side * math.radians(22), 0),
        )

    root["character_id"] = "char_shadow_creature_v2"
    root["identity_locked"] = True
    root["design"] = "cinematic_shadow_antagonist"

    return root


def build_blue_star(location=(0, 0, 2.9)):
    star_mat = material(
        "BLUE_STAR_V2",
        (0.03, 0.25, 1.0),
        roughness=0.2,
        emission=(0.08, 0.45, 1.0),
    )
    star = add_uv(
        "PROP_BLUE_STAR",
        location,
        (0.22, 0.22, 0.22),
        star_mat,
    )
    star["prop_id"] = "prop_blue_star_v2"
    star["identity_locked"] = True
    return star


def apply_emotion(root_name, emotion="neutral"):
    root = bpy.data.objects.get(root_name)
    if not root:
        return

    emotion = str(emotion).lower()

    # Lightweight pose language that works without Blender-version-
    # specific animation APIs.
    if emotion in ("curious", "wonder", "surprised"):
        root.rotation_euler.y = math.radians(-8)
    elif emotion in ("fear", "afraid", "worried"):
        root.rotation_euler.y = math.radians(7)
    elif emotion in ("courage", "brave", "determined"):
        root.rotation_euler.y = math.radians(-3)
    elif emotion in ("compassion", "sad", "gentle"):
        root.rotation_euler.y = math.radians(5)
    elif emotion in ("threat", "angry"):
        root.rotation_euler.y = math.radians(-5)
    else:
        root.rotation_euler.y = 0.0


def direct_character_gaze(root_name, target):
    root = bpy.data.objects.get(root_name)
    if not root:
        return

    direction = Vector(target) - root.location
    if direction.length > 0.001:
        root.rotation_euler = direction.to_track_quat("Y", "Z").to_euler()
