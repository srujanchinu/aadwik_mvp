"""
Aadwik Character Automation - v3
Blender 5.2.1 + MPFB 2.0.17 + Rigify

This version fixes the clothing-weight transfer:
- Uses the nearest BODY SURFACE TRIANGLE, not 3 nearest body vertices.
- Interpolates the body's actual DEF weights at that surface point.
- Keeps the strongest influences and NORMALIZES them.
- With --transfer-weights, ALL character clothing is reweighted, including
  clothing that already has DEF groups. This is important for repairing
  previously bad weights.
- Never edits bones, constraints, drivers, or Rigify widgets.
- Never overwrites the source .blend. Saves to the next _vN file.
- Creates a timestamped backup before applying changes.

Run:
blender.exe -b "<source>.blend" --python aadwik_character_automation.py -- --apply --transfer-weights
"""

import sys
import re
import json
import shutil
import hashlib
import argparse
import traceback
from pathlib import Path
from datetime import datetime

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

SOURCE_BLEND = Path(
    r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v2.blend"
)
RIG_NAME = "Aadwik_Main_Rig"
BODY_NAME = "Human"
ASSET_COLLECTION = "Aadwik_Character_Asset"
VERSION_RE = re.compile(r"^(?P<base>.+_v)(?P<n>\d+)\.blend$", re.IGNORECASE)

BODY_PART_KEYWORDS = ("eye", "brow", "lash", "teeth", "tongue", "hair")

# Clothing weighting controls.
MAX_INFLUENCES = 4
MIN_WEIGHT = 0.001


# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

class Log:
    def __init__(self):
        self.lines = []
        self.warnings = []
        self.errors = []

    def _emit(self, level, msg):
        line = f"[{datetime.now():%H:%M:%S}] [{level:<5}] {msg}"
        print(line, flush=True)
        self.lines.append(line)

    def step(self, msg):
        self._emit("STEP", msg)

    def info(self, msg):
        self._emit("INFO", msg)

    def ok(self, msg):
        self._emit("OK", msg)

    def warn(self, msg):
        self.warnings.append(msg)
        self._emit("WARN", msg)

    def error(self, msg):
        self.errors.append(msg)
        self._emit("ERROR", msg)


log = Log()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")


# ---------------------------------------------------------------------------
# ARGUMENTS
# ---------------------------------------------------------------------------

def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    p = argparse.ArgumentParser(prog="aadwik_character_automation")
    p.add_argument(
        "--apply",
        action="store_true",
        help="Perform changes. Without this the script is read-only."
    )
    p.add_argument(
        "--transfer-weights",
        action="store_true",
        help="Rebuild clothing DEF weights from the nearest body surface."
    )
    p.add_argument(
        "--force-save",
        action="store_true",
        help="Save a new version even if no changes were detected."
    )
    p.add_argument(
        "--no-save",
        action="store_true",
        help="Apply in memory but do not save a blend."
    )
    p.add_argument(
        "--source",
        type=str,
        default=None,
        help="Override the source .blend path."
    )
    return p.parse_args(argv)


# ---------------------------------------------------------------------------
# FILE LOAD / BACKUP
# ---------------------------------------------------------------------------

def ensure_file_loaded(override):
    target = Path(override) if override else SOURCE_BLEND

    if not target.exists():
        raise FileNotFoundError(f"Source .blend not found: {target}")

    current = Path(bpy.data.filepath) if bpy.data.filepath else None

    if current is None or current.resolve() != target.resolve():
        log.info(f"Opening {target}")
        bpy.ops.wm.open_mainfile(filepath=str(target))
    else:
        log.info(f"Already loaded: {target}")

    return target


def make_backup(src):
    backup_dir = src.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    dst = backup_dir / f"{src.stem}_backup_{TS}.blend"
    shutil.copy2(src, dst)

    log.ok(f"Backup written: {dst}")
    return dst


def next_version_path(src):
    m = VERSION_RE.match(src.name)

    if m:
        base = m.group("base")
        n = int(m.group("n"))
    else:
        base = src.stem + "_v"
        n = 1

    n += 1

    while (src.parent / f"{base}{n}.blend").exists():
        n += 1

    return src.parent / f"{base}{n}.blend"


# ---------------------------------------------------------------------------
# RIG INSPECTION / SAFETY FINGERPRINT
# ---------------------------------------------------------------------------

def find_rig():
    rig = bpy.data.objects.get(RIG_NAME)

    if rig and rig.type == "ARMATURE":
        return rig

    candidates = [
        o for o in bpy.data.objects
        if o.type == "ARMATURE" and o.data.get("rig_id")
    ]

    if len(candidates) == 1:
        log.warn(f"Using '{candidates[0].name}' as the main Rigify armature.")
        return candidates[0]

    log.error(
        f"Cannot identify main rig safely ({len(candidates)} Rigify candidates)."
    )
    return None


def rig_fingerprint(rig):
    h = hashlib.sha256()

    bone_names = sorted(b.name for b in rig.data.bones)
    h.update("|".join(bone_names).encode("utf-8"))

    constraint_count = 0

    for pb in sorted(rig.pose.bones, key=lambda p: p.name):
        for c in pb.constraints:
            constraint_count += 1
            target = getattr(c, "target", None)

            h.update(
                f"{pb.name}:{c.name}:{c.type}:"
                f"{target.name if target else ''}:"
                f"{getattr(c, 'subtarget', '')}:{c.mute}".encode("utf-8")
            )

    driver_count = (
        len(rig.animation_data.drivers)
        if rig.animation_data else 0
    )

    h.update(f"drivers:{driver_count}".encode("utf-8"))

    return {
        "hash": h.hexdigest(),
        "bones": len(bone_names),
        "constraints": constraint_count,
        "drivers": driver_count,
    }


def inspect_rigify(rig):
    names = [b.name for b in rig.data.bones]

    ik_fk_props = []

    for pb in rig.pose.bones:
        for key in pb.keys():
            low = key.lower()
            if "ik_fk" in low or "ik_stretch" in low:
                ik_fk_props.append(f"{pb.name}[{key}]")

    return {
        "rigify_rig_id": rig.data.get("rig_id"),
        "bones_total": len(names),
        "DEF": [n for n in names if n.startswith("DEF-")],
        "ORG": sum(n.startswith("ORG-") for n in names),
        "MCH": sum(n.startswith("MCH-") for n in names),
        "ik_fk_props": ik_fk_props,
        "custom_shapes": {
            pb.custom_shape for pb in rig.pose.bones if pb.custom_shape
        },
    }


# ---------------------------------------------------------------------------
# CHARACTER CLASSIFICATION
# ---------------------------------------------------------------------------

def is_widget(o, custom_shapes):
    if o.name.startswith("WGT-"):
        return True

    if o in custom_shapes:
        return True

    return False


def parent_chain(o):
    while o.parent:
        o = o.parent
        yield o


def belongs_to_character(o, rig, body):
    if o.name.startswith(BODY_NAME + "."):
        return True

    chain = list(parent_chain(o))

    if rig in chain or body in chain:
        return True

    return any(
        m.type == "ARMATURE" and m.object == rig
        for m in o.modifiers
    )


def classify(rig, rigify):
    body = bpy.data.objects.get(BODY_NAME)

    if body is None or body.type != "MESH":
        log.error(f"Body mesh '{BODY_NAME}' not found.")
        return None, [], [], []

    widgets = []
    attachments = []
    others = []

    for o in bpy.data.objects:
        if o in (rig, body):
            continue

        if is_widget(o, rigify["custom_shapes"]):
            widgets.append(o)

        elif o.type == "MESH" and belongs_to_character(o, rig, body):
            attachments.append(o)

        elif o.type == "MESH":
            others.append(o)

    return body, attachments, widgets, others


def category(o):
    name = o.name.lower()

    if any(k in name for k in BODY_PART_KEYWORDS):
        return "body_part"

    return "clothing"


# ---------------------------------------------------------------------------
# MESH ANALYSIS
# ---------------------------------------------------------------------------

def analyze_mesh(o, rig, def_names):
    arm_mods = [
        m for m in o.modifiers
        if m.type == "ARMATURE"
    ]

    def_idx = {
        vg.index
        for vg in o.vertex_groups
        if vg.name in def_names
    }

    if def_idx:
        unweighted = 0

        for v in o.data.vertices:
            if not any(
                g.group in def_idx and g.weight > 0.0
                for g in v.groups
            ):
                unweighted += 1
    else:
        unweighted = len(o.data.vertices)

    bone_parented = (
        o.parent == rig and
        o.parent_type == "BONE"
    )

    deform_names = {vg.name for vg in o.vertex_groups}

    missing_def = (
        sorted(def_names - deform_names)
        if o.name == BODY_NAME else []
    )

    rig_bone_names = {b.name for b in rig.data.bones}

    orphan = (
        sorted(
            n for n in deform_names
            if n not in rig_bone_names
        )
        if o.name == BODY_NAME else []
    )

    return {
        "name": o.name,
        "vertices": len(o.data.vertices),
        "parent": o.parent.name if o.parent else None,
        "parent_type": o.parent_type,
        "bone_parented": bone_parented,
        "armature_modifiers": [
            (
                m.name,
                m.object.name if m.object else None,
                m.use_vertex_groups
            )
            for m in arm_mods
        ],
        "armature_mod_ok": (
            bool(arm_mods) and
            arm_mods[0].object == rig and
            arm_mods[0].use_vertex_groups
        ),
        "def_groups": len(def_idx),
        "unweighted_vertices": unweighted,
        "missing_def_groups_on_body": missing_def,
        "orphan_groups_on_body": orphan,
        "shape_keys": (
            len(o.data.shape_keys.key_blocks)
            if o.data.shape_keys else 0
        ),
    }


# ---------------------------------------------------------------------------
# ARMATURE MODIFIER
# ---------------------------------------------------------------------------

def ensure_armature_modifier(o, rig, apply):
    mods = [
        m for m in o.modifiers
        if m.type == "ARMATURE"
    ]

    changes = 0

    if not mods:
        if not apply:
            log.info(
                f"[dry-run] would add Armature modifier -> "
                f"{rig.name} on '{o.name}'"
            )
            return 0

        m = o.modifiers.new("Armature", "ARMATURE")
        m.object = rig
        m.use_vertex_groups = True

        try:
            o.modifiers.move(len(o.modifiers) - 1, 0)
        except Exception:
            pass

        log.ok(
            f"Added Armature modifier -> {rig.name} on '{o.name}'"
        )
        return 1

    primary = mods[0]

    if primary.object != rig:
        if apply:
            log.ok(
                f"Retargeted '{o.name}' Armature modifier: "
                f"{primary.object.name if primary.object else None} "
                f"-> {rig.name}"
            )
            primary.object = rig
            changes += 1
        else:
            log.info(
                f"[dry-run] would retarget Armature modifier "
                f"on '{o.name}' to {rig.name}"
            )

    if not primary.use_vertex_groups:
        if apply:
            primary.use_vertex_groups = True
            changes += 1
            log.ok(
                f"Enabled vertex-group deformation on '{o.name}'"
            )

    if len(mods) > 1:
        log.warn(
            f"'{o.name}' has {len(mods)} Armature modifiers "
            f"(duplicates left untouched)"
        )

    return changes


# ---------------------------------------------------------------------------
# ROBUST BODY-SURFACE WEIGHT TRANSFER
# ---------------------------------------------------------------------------

def build_body_surface(body):
    """
    Build a triangle BVH from the ORIGINAL body mesh in body-local space.
    Every triangle stores the three original body vertex indices.
    """
    verts = [v.co.copy() for v in body.data.vertices]
    triangles = []
    tri_vertex_indices = []

    for poly in body.data.polygons:
        ids = list(poly.vertices)

        if len(ids) < 3:
            continue

        # Fan triangulation: (0,1,2), (0,2,3), ...
        for i in range(1, len(ids) - 1):
            tri = (ids[0], ids[i], ids[i + 1])
            triangles.append(tri)
            tri_vertex_indices.append(tri)

    if not triangles:
        raise RuntimeError("Body mesh has no usable triangles.")

    bvh = BVHTree.FromPolygons(
        verts,
        triangles,
        all_triangles=True
    )

    return bvh, tri_vertex_indices


def barycentric_weights(point, a, b, c):
    """
    Return barycentric coordinates of point relative to triangle ABC.
    Values are clamped and normalized for numerical safety.
    """
    v0 = b - a
    v1 = c - a
    v2 = point - a

    d00 = v0.dot(v0)
    d01 = v0.dot(v1)
    d11 = v1.dot(v1)
    d20 = v2.dot(v0)
    d21 = v2.dot(v1)

    denom = d00 * d11 - d01 * d01

    if abs(denom) < 1e-12:
        return (1.0, 0.0, 0.0)

    inv = 1.0 / denom

    v = (d11 * d20 - d01 * d21) * inv
    w = (d00 * d21 - d01 * d20) * inv
    u = 1.0 - v - w

    u = max(0.0, u)
    v = max(0.0, v)
    w = max(0.0, w)

    total = u + v + w

    if total <= 1e-12:
        return (1.0, 0.0, 0.0)

    return (u / total, v / total, w / total)


def collect_body_weights(body, def_names):
    """
    Cache only the body's DEF groups.
    """
    group_index_to_name = {
        vg.index: vg.name
        for vg in body.vertex_groups
        if vg.name in def_names
    }

    cache = {}

    for v in body.data.vertices:
        weights = {}

        for g in v.groups:
            name = group_index_to_name.get(g.group)

            if name is not None and g.weight > 0.0:
                weights[name] = g.weight

        cache[v.index] = weights

    return group_index_to_name, cache


def clear_target_def_weights(target, def_names):
    """
    Remove old DEF weights before rebuilding them.
    Non-DEF vertex groups are preserved.
    """
    for name in list(def_names):
        vg = target.vertex_groups.get(name)

        if vg is not None:
            target.vertex_groups.remove(vg)


def normalize_and_limit(weights):
    """
    Keep strongest influences, remove tiny values, then normalize.
    """
    filtered = [
        (name, value)
        for name, value in weights.items()
        if value > MIN_WEIGHT
    ]

    filtered.sort(key=lambda x: x[1], reverse=True)
    filtered = filtered[:MAX_INFLUENCES]

    total = sum(v for _, v in filtered)

    if total <= 1e-12:
        return []

    return [
        (name, value / total)
        for name, value in filtered
    ]


def transfer_weights_surface(body, target, def_names):
    """
    Transfer weights from body -> target using nearest surface triangle.

    This is much more stable than nearest-vertex averaging because clothing
    vertices receive weights from the exact nearby body surface location.
    """
    bvh, tri_indices = build_body_surface(body)
    _, body_weights = collect_body_weights(body, def_names)

    # Always rebuild all DEF groups on the target.
    clear_target_def_weights(target, def_names)

    target_groups = {}

    for name in sorted(def_names):
        target_groups[name] = target.vertex_groups.new(name=name)

    body_to_target = body.matrix_world
    target_to_body = body.matrix_world.inverted()
    target_world = target.matrix_world

    transferred_vertices = 0
    fallback_vertices = 0

    for v in target.data.vertices:
        world_point = target_world @ v.co
        body_local_point = target_to_body @ world_point

        nearest_co, _normal, tri_index, _distance = bvh.find_nearest(
            body_local_point
        )

        if tri_index < 0:
            fallback_vertices += 1
            continue

        i0, i1, i2 = tri_indices[tri_index]

        a = body.data.vertices[i0].co
        b = body.data.vertices[i1].co
        c = body.data.vertices[i2].co

        bary = barycentric_weights(
            nearest_co,
            a,
            b,
            c
        )

        w0 = body_weights.get(i0, {})
        w1 = body_weights.get(i1, {})
        w2 = body_weights.get(i2, {})

        names = set(w0) | set(w1) | set(w2)

        interpolated = {}

        for name in names:
            value = (
                w0.get(name, 0.0) * bary[0] +
                w1.get(name, 0.0) * bary[1] +
                w2.get(name, 0.0) * bary[2]
            )

            if value > 0.0:
                interpolated[name] = value

        final_weights = normalize_and_limit(interpolated)

        for name, value in final_weights:
            target_groups[name].add(
                [v.index],
                value,
                "REPLACE"
            )

        if final_weights:
            transferred_vertices += 1

    log.info(
        f"Surface weight transfer '{body.name}' -> '{target.name}': "
        f"{transferred_vertices}/{len(target.data.vertices)} vertices"
    )

    if fallback_vertices:
        log.warn(
            f"'{target.name}': {fallback_vertices} vertices "
            f"had no BVH triangle result."
        )

    return len(target_groups), transferred_vertices


# ---------------------------------------------------------------------------
# ASSET COLLECTION
# ---------------------------------------------------------------------------

def ensure_asset_collection(rig, body, members):
    changes = 0

    col = bpy.data.collections.get(ASSET_COLLECTION)

    if col is None:
        col = bpy.data.collections.new(ASSET_COLLECTION)
        bpy.context.scene.collection.children.link(col)

        log.ok(
            f"Created collection '{ASSET_COLLECTION}'"
        )
        changes += 1

    for o in [rig, body] + members:
        if o.name not in col.objects:
            col.objects.link(o)
            changes += 1

    metadata = {
        "aadwik_schema": 2,
        "aadwik_rig": rig.name,
        "aadwik_body": body.name,
        "aadwik_members": json.dumps(
            sorted(o.name for o in members)
        ),
        "aadwik_weight_method": "nearest_body_surface_barycentric",
        "aadwik_max_influences": MAX_INFLUENCES,
    }

    for key, value in metadata.items():
        if col.get(key) != value:
            col[key] = value
            changes += 1

    return changes


# ---------------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------------

def write_reports(src, report):
    report_dir = src.parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = (
        report_dir /
        f"aadwik_validation_{TS}.json"
    )

    text_path = (
        report_dir /
        f"aadwik_validation_{TS}.txt"
    )

    json_path.write_text(
        json.dumps(
            report,
            indent=2,
            default=str
        ),
        encoding="utf-8"
    )

    text_path.write_text(
        "\n".join(log.lines),
        encoding="utf-8"
    )

    log.ok(f"Report JSON: {json_path}")
    log.ok(f"Report log : {text_path}")

    return json_path, text_path


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    apply = args.apply

    log.step("PHASE 0 - Load file")
    log.info(
        f"Blender {bpy.app.version_string} | "
        f"mode = {'APPLY' if apply else 'DRY-RUN (read-only)'}"
    )

    src = ensure_file_loaded(args.source)

    log.step("PHASE 1 - Inspect scene")

    rig = find_rig()

    if rig is None:
        return finish(src, {}, False)

    rigify = inspect_rigify(rig)

    log.info(
        f"Rig '{rig.name}': "
        f"{rigify['bones_total']} bones | "
        f"DEF={len(rigify['DEF'])} "
        f"ORG={rigify['ORG']} "
        f"MCH={rigify['MCH']} | "
        f"rig_id={rigify['rigify_rig_id']}"
    )

    log.info(
        f"IK/FK switch properties found: "
        f"{len(rigify['ik_fk_props'])}"
    )

    if not rigify["DEF"]:
        log.error(
            "Rig has no DEF- bones; refusing to continue."
        )
        return finish(src, {}, False)

    body, attachments, widgets, others = classify(
        rig,
        rigify
    )

    if body is None:
        return finish(src, {}, False)

    clothing = [
        o for o in attachments
        if category(o) == "clothing"
    ]

    parts = [
        o for o in attachments
        if category(o) == "body_part"
    ]

    log.info(
        f"Body: {body.name} | "
        f"clothing: {[o.name for o in clothing]} | "
        f"body parts: {[o.name for o in parts]}"
    )

    log.info(
        f"Rigify widgets ignored: {len(widgets)} | "
        f"unrelated meshes: {[o.name for o in others]}"
    )

    def_names = set(rigify["DEF"])

    fp_before = rig_fingerprint(rig)

    log.info(
        f"Rig fingerprint BEFORE: {fp_before}"
    )

    backup = None

    if apply:
        log.step("Backup")
        backup = make_backup(src)

    log.step(
        "PHASE 2 - Character & clothing deformation"
    )

    changes = 0

    targets = [body] + attachments

    for o in targets:
        analysis = analyze_mesh(
            o,
            rig,
            def_names
        )

        log.info(
            f"'{o.name}': "
            f"armature_mod_ok={analysis['armature_mod_ok']} "
            f"def_groups={analysis['def_groups']} "
            f"unweighted="
            f"{analysis['unweighted_vertices']}/"
            f"{analysis['vertices']} "
            f"bone_parented="
            f"{analysis['bone_parented']}"
        )

        if analysis["bone_parented"]:
            log.info(
                f"'{o.name}' is bone-parented to "
                f"{o.parent_bone}; modifier not required."
            )
            continue

        changes += ensure_armature_modifier(
            o,
            rig,
            apply
        )

        # IMPORTANT:
        # Re-transfer ALL clothing when --transfer-weights is supplied.
        # This repairs clothing that already had bad DEF weights.
        if o is not body and category(o) == "clothing":
            if apply and args.transfer_weights:
                group_count, vertex_count = transfer_weights_surface(
                    body,
                    o,
                    def_names
                )

                log.ok(
                    f"Rebuilt DEF weights for '{o.name}': "
                    f"{group_count} groups, "
                    f"{vertex_count}/{len(o.data.vertices)} vertices"
                )

                changes += 1

            elif analysis["def_groups"] == 0:
                log.warn(
                    f"'{o.name}' has NO DEF groups. "
                    f"Use --apply --transfer-weights."
                )

    log.step("PHASE 2b - Asset organisation")

    if apply:
        changes += ensure_asset_collection(
            rig,
            body,
            attachments
        )
    else:
        log.info(
            f"[dry-run] would ensure collection "
            f"'{ASSET_COLLECTION}'"
        )

    log.step("PHASE 3 - Rig validation")

    fp_after = rig_fingerprint(rig)

    rig_intact = (
        fp_before["hash"] ==
        fp_after["hash"]
    )

    if rig_intact:
        log.ok(
            "Rig integrity "
            "(bones/constraints/drivers unchanged): PASS"
        )
    else:
        log.error(
            "Rig integrity "
            "(bones/constraints/drivers unchanged): FAIL"
        )

    results = {}

    for o in targets:
        analysis = analyze_mesh(
            o,
            rig,
            def_names
        )

        results[o.name] = analysis

        status = "PASS"

        if not analysis["bone_parented"]:
            if (
                not analysis["armature_mod_ok"] or
                analysis["def_groups"] == 0
            ):
                status = "FAIL"
            elif (
                o is body and
                analysis["unweighted_vertices"] > 0
            ):
                status = "WARN"

        analysis["status"] = status

        if status == "PASS":
            log.ok(f"  {o.name}: PASS")
        elif status == "WARN":
            log.warn(f"  {o.name}: WARN")
        else:
            log.error(f"  {o.name}: FAIL")

    body_result = results[body.name]

    if body_result["missing_def_groups_on_body"]:
        log.warn(
            f"Body missing "
            f"{len(body_result['missing_def_groups_on_body'])} "
            f"DEF groups (normal for unweighted face/utility bones): "
            f"{body_result['missing_def_groups_on_body'][:8]}..."
        )

    if body_result["orphan_groups_on_body"]:
        log.info(
            f"Body has "
            f"{len(body_result['orphan_groups_on_body'])} "
            f"vertex groups with no matching bone "
            f"(left untouched)"
        )

    all_pass = (
        rig_intact and
        all(
            result["status"] != "FAIL"
            for result in results.values()
        )
    )

    report = {
        "timestamp": TS,
        "blender": bpy.app.version_string,
        "mode": "apply" if apply else "dry-run",
        "source": str(src),
        "backup": str(backup) if backup else None,
        "rig": rig.name,
        "rig_fingerprint_before": fp_before,
        "rig_fingerprint_after": fp_after,
        "rig_intact": rig_intact,
        "rigify": {
            k: v
            for k, v in rigify.items()
            if k != "custom_shapes"
        },
        "widgets_ignored": len(widgets),
        "weight_method": "nearest_body_surface_barycentric",
        "max_influences": MAX_INFLUENCES,
        "meshes": results,
        "changes_made": changes,
        "overall": "PASS" if all_pass else "FAIL",
    }

    saved = None

    if apply and not args.no_save:
        if not rig_intact:
            log.error(
                "Rig changed unexpectedly - NOT saving. "
                "Source file remains untouched."
            )

        elif changes == 0 and not args.force_save:
            log.info(
                "No changes needed - nothing saved."
            )

        else:
            output = next_version_path(src)

            bpy.ops.wm.save_as_mainfile(
                filepath=str(output),
                copy=True
            )

            if (
                output.exists() and
                output.stat().st_size > 0
            ):
                saved = output
                log.ok(
                    f"Saved new version: {output}"
                )
            else:
                log.error(
                    f"Save failed: {output}"
                )

    report["saved_version"] = (
        str(saved) if saved else None
    )

    return finish(
        src,
        report,
        all_pass
    )


def finish(src, report, ok):
    log.step("Report")

    if report:
        write_reports(
            src,
            report
        )

    log.info(
        f"OVERALL: "
        f"{'PASS' if ok else 'FAIL'} | "
        f"warnings={len(log.warnings)} "
        f"errors={len(log.errors)}"
    )

    return 0 if ok else 2


if __name__ == "__main__":
    code = 1

    try:
        code = main()

    except Exception:
        log.error(
            "Unhandled exception:\n" +
            traceback.format_exc()
        )

    if bpy.app.background:
        sys.exit(code)
