import bpy
from mathutils import Vector
import sys
import os
import ast
import argparse
from pathlib import Path


print("[AADWIK RIGIFY V3 FIX] START")


# ---------------------------------------------------------
# ARGUMENTS
# ---------------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument("--source", required=True)
parser.add_argument("--blend_out", required=True)
parser.add_argument("--width", type=int, default=640)
parser.add_argument("--height", type=int, default=640)

# Blender passes its own arguments before "--".
# Parse only the arguments after the separator.
if "--" in sys.argv:
    blender_args = sys.argv[sys.argv.index("--") + 1:]
else:
    blender_args = []

args = parser.parse_args(blender_args)


SOURCE = Path(args.source)
BLEND_OUT = Path(args.blend_out)

print("[AADWIK RIGIFY V3 FIX] SOURCE:", SOURCE)
print("[AADWIK RIGIFY V3 FIX] OUTPUT:", BLEND_OUT)


# ---------------------------------------------------------
# CLEAN SCENE
# ---------------------------------------------------------

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

for datablocks in (
    bpy.data.meshes,
    bpy.data.curves,
    bpy.data.materials,
    bpy.data.cameras,
    bpy.data.lights,
):
    for block in list(datablocks):
        try:
            datablocks.remove(block)
        except Exception:
            pass


# ---------------------------------------------------------
# VERIFY RIGIFY
# ---------------------------------------------------------

# ---------------------------------------------------------
# ENABLE RIGIFY EXPLICITLY
# ---------------------------------------------------------

print("[AADWIK RIGIFY V3 FIX] Enabling Rigify add-on...")

try:
    bpy.ops.preferences.addon_enable(module="rigify")
    print("[AADWIK RIGIFY V3 FIX] Rigify add-on enabled")
except Exception as e:
    print("[AADWIK RIGIFY V3 FIX] addon_enable returned:", repr(e))

# Import after enabling so registration is completed.
try:
    import rigify
    print("[AADWIK RIGIFY V3 FIX] Rigify module imported")
except Exception as e:
    raise RuntimeError(
        "Rigify could not be imported."
    ) from e


# Force registration if the operator is still unavailable.
if not hasattr(bpy.ops.armature, "metarig_add"):

    print(
        "[AADWIK RIGIFY V3 FIX] metarig_add not registered; "
        "reloading Rigify..."
    )

    try:
        import importlib
        importlib.reload(rigify)
    except Exception as e:
        print(
            "[AADWIK RIGIFY V3 FIX] Rigify reload warning:",
            repr(e)
        )


if not hasattr(bpy.ops.armature, "metarig_add"):
    raise RuntimeError(
        "Rigify Human Meta-Rig operator is still unavailable "
        "in Blender background mode."
    )

print(
    "[AADWIK RIGIFY V3 FIX] "
    "Rigify Human Meta-Rig operator available"
)


# ---------------------------------------------------------
# LOAD V3 CHARACTER SOURCE SAFELY
# ---------------------------------------------------------

if not SOURCE.exists():
    raise FileNotFoundError(f"V3 character source not found: {SOURCE}")

source_text = SOURCE.read_text(encoding="utf-8")

print("[AADWIK RIGIFY V3 FIX] Parsing V3 character source...")


# Parse the complete file first.
tree = ast.parse(source_text, filename=str(SOURCE))


# ---------------------------------------------------------
# REMOVE COMMAND-LINE EXECUTION ONLY
# ---------------------------------------------------------
#
# We keep the character-building functions/classes/imports.
#
# We remove:
#   - argparse CLI execution
#   - parse_args()
#   - if __name__ == "__main__": ...
#
# This avoids the previous broken string-cut approach.
# ---------------------------------------------------------

new_body = []


def contains_argparse(node):
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id == "argparse":
            return True
        if isinstance(child, ast.Attribute):
            if child.attr in (
                "ArgumentParser",
                "parse_args",
                "parse_known_args",
            ):
                return True
    return False


def is_main_guard(node):
    if not isinstance(node, ast.If):
        return False

    test = node.test

    if not isinstance(test, ast.Compare):
        return False

    if not isinstance(test.left, ast.Name):
        return False

    if test.left.id != "__name__":
        return False

    return True


for node in tree.body:

    # Remove __main__ execution block.
    if is_main_guard(node):
        print("[AADWIK RIGIFY V3 FIX] Removed __main__ execution block")
        continue

    # Remove obvious top-level argparse CLI statements.
    if contains_argparse(node):
        print(
            "[AADWIK RIGIFY V3 FIX] Removed CLI/argparse statement:",
            type(node).__name__,
        )
        continue

    new_body.append(node)


tree.body = new_body

ast.fix_missing_locations(tree)


# ---------------------------------------------------------
# EXECUTE CHARACTER DEFINITIONS
# ---------------------------------------------------------

namespace = {
    "__name__": "aadwik_maya_character_v3_asset",
    "__file__": str(SOURCE),
}

compiled = compile(
    tree,
    filename=str(SOURCE),
    mode="exec",
)

exec(compiled, namespace, namespace)

print("[AADWIK RIGIFY V3 FIX] V3 character definitions loaded")

# Build the actual V3 character.
build_maya = namespace.get("build_maya")

if not callable(build_maya):
    raise RuntimeError(
        "V3 build_maya() function was not found."
    )

print("[AADWIK RIGIFY V3 FIX] Calling build_maya()...")

build_maya()

print("[AADWIK RIGIFY V3 FIX] V3 character created")


# ---------------------------------------------------------
# FIND V3 CHARACTER OBJECTS
# ---------------------------------------------------------

objects = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "MESH"
]


if not objects:
    raise RuntimeError(
        "V3 source loaded, but no character mesh objects were created."
    )


print(
    "[AADWIK RIGIFY V3 FIX] Mesh objects found:",
    len(objects)
)


# ---------------------------------------------------------
# CHARACTER BOUNDS
# ---------------------------------------------------------

min_x = float("inf")
min_y = float("inf")
min_z = float("inf")

max_x = float("-inf")
max_y = float("-inf")
max_z = float("-inf")


for obj in objects:

    for corner in obj.bound_box:

        world_corner = obj.matrix_world @ Vector(corner)

        min_x = min(min_x, world_corner.x)
        min_y = min(min_y, world_corner.y)
        min_z = min(min_z, world_corner.z)

        max_x = max(max_x, world_corner.x)
        max_y = max(max_y, world_corner.y)
        max_z = max(max_z, world_corner.z)


# ---------------------------------------------------------
# IMPORT VECTOR SAFELY
# ---------------------------------------------------------

from mathutils import Vector


# Recalculate bounds using Vector.
min_x = float("inf")
min_y = float("inf")
min_z = float("inf")

max_x = float("-inf")
max_y = float("-inf")
max_z = float("-inf")


for obj in objects:

    for corner in obj.bound_box:

        world_corner = obj.matrix_world @ Vector(corner)

        min_x = min(min_x, world_corner.x)
        min_y = min(min_y, world_corner.y)
        min_z = min(min_z, world_corner.z)

        max_x = max(max_x, world_corner.x)
        max_y = max(max_y, world_corner.y)
        max_z = max(max_z, world_corner.z)


height = max_z - min_z

print(
    "[AADWIK RIGIFY V3 FIX] CHARACTER HEIGHT:",
    round(height, 3),
)


# ---------------------------------------------------------
# CENTER CHARACTER
# ---------------------------------------------------------

center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2


for obj in objects:
    obj.location.x -= center_x
    obj.location.y -= center_y
    obj.location.z -= min_z


# ---------------------------------------------------------
# CREATE HUMAN METARIG
# ---------------------------------------------------------

print("[AADWIK RIGIFY V3 FIX] Creating Human Meta-Rig...")

bpy.ops.object.select_all(action="DESELECT")

# Create a plain armature object.
arm_data = bpy.data.armatures.new("MAYA_RIGIFY_METARIG_V3_DATA")
metarig = bpy.data.objects.new(
    "MAYA_RIGIFY_METARIG_V3",
    arm_data,
)

bpy.context.collection.objects.link(metarig)

bpy.context.view_layer.objects.active = metarig
metarig.select_set(True)

# Build the official Blender/Rigify Human Meta-Rig
# directly from Rigify's generated Human definition.
from rigify.metarigs import human

human.create(metarig)

print(
    "[AADWIK RIGIFY V3 FIX] "
    "Human Meta-Rig created directly"
)

metarig.name = "MAYA_RIGIFY_METARIG_V3"


print(
    "[AADWIK RIGIFY V3 FIX] METARIG:",
    metarig.name,
)


# ---------------------------------------------------------
# SCALE METARIG TO CHARACTER
# ---------------------------------------------------------

meta_height = 0.0

for bone in metarig.data.bones:

    head = metarig.matrix_world @ bone.head_local
    tail = metarig.matrix_world @ bone.tail_local

    meta_height = max(
        meta_height,
        head.z,
        tail.z,
    )


metarig


# ---------------------------------------------------------
# PLACE METARIG
# ---------------------------------------------------------

metarig.location.x = 0
metarig.location.y = 0
metarig.location.z = 0


# ---------------------------------------------------------
# SAVE CHECKPOINT
# ---------------------------------------------------------

BLEND_OUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

metarig_path = BLEND_OUT.with_name(
    BLEND_OUT.stem + "_METARIG.blend"
)

bpy.ops.wm.save_as_mainfile(
    filepath=str(metarig_path)
)

print(
    "[AADWIK RIGIFY V3 FIX] METARIG CHECKPOINT:",
    metarig_path,
)


# ---------------------------------------------------------
# FINAL SAVE
# ---------------------------------------------------------

bpy.ops.wm.save_as_mainfile(
    filepath=str(BLEND_OUT)
)

print(
    "[AADWIK RIGIFY V3 FIX] CHARACTER + METARIG READY"
)

print(
    "[AADWIK RIGIFY V3 FIX] CHECKPOINT:",
    BLEND_OUT
)

print(
    "[AADWIK RIGIFY V3 FIX] STOPPING BEFORE RIG GENERATION"
)

print("[AADWIK RIGIFY V3 FIX] COMPLETE")