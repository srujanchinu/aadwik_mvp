import bpy
import json
import math
import argparse
import sys
from pathlib import Path
from mathutils import Vector
import os
import sys

PROVIDER_DIR = os.path.dirname(os.path.abspath(__file__))
if PROVIDER_DIR not in sys.path:
    sys.path.insert(0, PROVIDER_DIR)

from aadwik_character_quality import (
    build_tara,
    build_guardian,
    build_shadow,
    build_blue_star,
    apply_emotion,
)


def mat(name, color, metallic=0.0, rough=0.6, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value = (*color, 1)
        bs.inputs["Roughness"].default_value = rough
        bs.inputs["Metallic"].default_value = metallic
        if emission:
            bs.inputs["Emission Color"].default_value = (*emission, 1)
            bs.inputs["Emission Strength"].default_value = 4
    return m


def cube(name, loc, scale, material, bevel=.08):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new("Soft edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    o.data.materials.append(material)
    return o


def uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=12, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return o


def cyl(name, loc, radius, depth, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=radius, depth=depth,
        location=loc, rotation=rot
    )
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    return o


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def normalize_location(location):
    if isinstance(location, dict):
        kind = location.get("kind", "fantasy")
    elif isinstance(location, str):
        kind = location
    else:
        kind = "fantasy"

    kind = str(kind or "fantasy").strip().lower()

    aliases = {
        "village_festival": "village",
        "festival": "village",
        "forest_moonlit": "forest",
        "moonlit_forest": "forest",
        "ancient_tree": "forest",
        "tree": "forest",
        "glowing_river": "river",
        "ancient_temple": "temple",
        "village_home": "home",
        "magical_forest": "forest",
    }
    return aliases.get(kind, kind)


def environment(kind):
    ground = mat("ground", (0.06, 0.08, 0.10))

    if kind == "village":
        cube("ground", (0, 0, -.15), (7, 5, .15), ground)
        wood = mat("wood", (.30, .16, .08))
        roof = mat("roof", (.08, .04, .03))
        warm = mat("lantern", (1.0, .35, .08), emission=(1.0, .12, .02))
        for x in (-4, -2, 2, 4):
            cube("house", (x, 1, 1.0), (1.0, .8, 1.1), wood)
            cube("roof", (x, 1, 2.25), (1.2, .95, .18), roof)
        for x in (-4, -2, 0, 2, 4):
            uv("lantern", (x, -.7, 2.5), (.10, .10, .18), warm)

    elif kind == "forest":
        cube("ground", (0, 0, -.15), (7, 5, .15),
             mat("forest_ground", (.035, .12, .055)))
        trunk = mat("trunk", (.20, .09, .035))
        leaf = mat("leaf", (.03, .22, .08))
        for x in (-5, -3, -1, 1, 3, 5):
            h = 2.2 + (abs(x) % 2)
            cyl("tree", (x, 1, h / 2), .22, h, trunk)
            uv("canopy", (x, 1, h + .5), (1.0, 1.0, .9), leaf)

    elif kind == "river":
        cube("bank", (0, 1.8, -.1), (7, 1.2, .12),
             mat("bank", (.08, .18, .08)))
        cube("water", (0, 0, -.05), (7, .9, .08),
             mat("water", (.02, .18, .38), metallic=.2))
        rock = mat("rock", (.18, .20, .22))
        for x in (-5, -3, 3, 5):
            uv("rock", (x, .8, .15), (.45, .30, .20), rock)

    elif kind == "temple":
        stone = mat("stone", (.18, .18, .20))
        stone2 = mat("stone2", (.28, .27, .25))
        cube("floor", (0, 0, -.15), (7, 5, .15), stone)
        for x in (-4, -2, 2, 4):
            cyl("column", (x, 0, 1.6), .35, 3.2, stone2)
        cube("back", (0, 2.2, 2.2), (5, .3, 2.4), stone2)
        cube("altar", (0, 0, .45), (1, .7, .35),
             mat("altar", (.22, .14, .08)))

    elif kind == "home":
        cube("floor", (0, 0, -.15), (6, 5, .15),
             mat("homefloor", (.25, .16, .09)))
        cube("wall", (0, 2, 2), (5, .2, 2),
             mat("wall", (.65, .45, .25)))

    else:
        cube("ground", (0, 0, -.15), (7, 5, .15), ground)


def setup_world(kind):
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if not bg:
        return

    if kind == "home":
        color = (.25, .12, .04, 1)
    elif kind == "village":
        color = (.10, .04, .02, 1)
    else:
        color = (.008, .012, .035, 1)

    bg.inputs["Color"].default_value = color
    bg.inputs["Strength"].default_value = .25


def add_lights(kind):
    bpy.ops.object.light_add(type="AREA", location=(0, -3, 7))
    key = bpy.context.object
    key.data.energy = 1000
    key.data.shape = "DISK"
    key.data.size = 5

    bpy.ops.object.light_add(type="AREA", location=(4, 2, 4))
    fill = bpy.context.object
    fill.data.energy = 450
    fill.data.size = 4

    if kind in ("forest", "river", "temple"):
        bpy.ops.object.light_add(type="POINT", location=(0, 0, 2.5))
        point = bpy.context.object
        point.data.energy = 500
        point.data.color = (.15, .35, 1.0)


def camera_for(scene_index, shot_type="wide"):
    bpy.ops.object.camera_add(location=(0, -10, 4.0))
    cam = bpy.context.object

    if shot_type == "close":
        cam.data.lens = 68
        cam.location.y = -7.0
        cam.location.z = 3.0
    elif shot_type == "medium":
        cam.data.lens = 55
        cam.location.y = -8.5
        cam.location.z = 3.3
    else:
        cam.data.lens = 48

    target = Vector((0, 0, 1.4))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return cam


def scene_characters(scene_data):
    chars = scene_data.get("characters", [])
    if not isinstance(chars, list):
        chars = []

    ids = []
    for item in chars:
        if isinstance(item, str):
            ids.append(item.lower())
        elif isinstance(item, dict):
            ids.append(str(
                item.get("id")
                or item.get("name")
                or item.get("kind")
                or ""
            ).lower())

    tara = build_tara((-1.4, 0, 0))
    guardian = None
    shadow = None

    # For the Last Star and compatible story plans, use the locked
    # character identities whenever they are present.
    if any(x in ids for x in ("guardian", "story_creature", "creature")):
        guardian = build_guardian((1.0, 0, 1.0))

    if "shadow_creature" in ids:
        shadow = build_shadow((1.7, 0, 0))

    return tara, guardian, shadow


def add_star_if_needed(scene_data, start_frame):
    props = scene_data.get("props", [])
    if not isinstance(props, list):
        return None

    wants_star = False
    for item in props:
        if isinstance(item, str):
            kind = item
        elif isinstance(item, dict):
            kind = item.get("kind", item.get("type", ""))
        else:
            kind = ""
        if str(kind).lower() in ("star", "blue_star", "magical_star"):
            wants_star = True

    if not wants_star:
        return None

    star = build_blue_star((0, 0, 2.9))
    star.keyframe_insert("location", frame=start_frame)
    star.location.z = 3.5
    star.keyframe_insert("location", frame=start_frame + 12)
    return star


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--fps", type=int, default=8)
    parsed = parser.parse_args(args)

    plan = json.loads(
        Path(parsed.plan).read_text(encoding="utf-8")
    )
    out = Path(parsed.out)
    out.mkdir(parents=True, exist_ok=True)

    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = parsed.width
    sc.render.resolution_y = parsed.height
    sc.render.resolution_percentage = 100
    sc.render.fps = parsed.fps
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False

    scenes = plan.get("scenes", [])
    if not isinstance(scenes, list):
        raise RuntimeError("Production plan scenes must be a list.")

    frame = 1

    for scene_index, scene_data in enumerate(scenes, 1):
        clear()

        kind = normalize_location(
            scene_data.get("location", "fantasy")
        )

        print(
            "[AADWIK 23] SCENE",
            scene_index,
            "LOCATION:",
            kind,
            flush=True,
        )

        environment(kind)
        setup_world(kind)
        add_lights(kind)

        tara, guardian, shadow = scene_characters(scene_data)

        emotion = scene_data.get(
            "emotion",
            scene_data.get("emotional_state", "neutral")
        )

        apply_emotion(
            "CHAR_TARA_ROOT",
            emotion
        )

        if guardian:
            apply_emotion(
                "CHAR_GUARDIAN_ROOT",
                emotion
            )

        if shadow:
            apply_emotion(
                "CHAR_SHADOW_ROOT",
                "threat"
            )

        start = frame
        end = frame + 15

        add_star_if_needed(
            scene_data,
            start
        )

        # Story-aware shot language.
        text = " ".join([
            str(scene_data.get("title", "")),
            str(scene_data.get("story_context", "")),
            str(scene_data.get("description", "")),
        ]).lower()

        if any(x in text for x in (
            "discover", "reveals", "revelation", "emotion",
            "compassion", "courage", "confront", "injured"
        )):
            shot_type = "close"
        elif any(x in text for x in (
            "journey", "festival", "river", "forest"
        )):
            shot_type = "wide"
        else:
            shot_type = "medium"

        cam = camera_for(
            scene_index,
            shot_type
        )
        sc.camera = cam

        # Cinematic camera move.
        cam.location.x = -4.5 if scene_index % 2 else 4.5
        cam.keyframe_insert("location", frame=start)

        cam.location.x = 4.5 if scene_index % 2 else -4.5
        cam.keyframe_insert("location", frame=end)

        # Natural hero movement.
        tara.location.x = -1.0
        tara.keyframe_insert("location", frame=start)

        tara.location.x = -.15
        tara.keyframe_insert("location", frame=end)

        for f in range(start, end + 1):
            sc.frame_set(f)
            sc.render.filepath = str(
                out / f"frame_{f:06d}.png"
            )
            bpy.ops.render.render(
                write_still=True
            )

        frame = end + 1

    print(
        "[AADWIK 23] COMPLETE",
        frame - 1,
        "frames",
        flush=True,
    )


if __name__ == "__main__":
    main()
