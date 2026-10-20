"""
AADWIK Character Refinement Inspector
Blender 5.2.x | Non-destructive inspection pass

This script DOES NOT modify or save the source .blend.
It opens the selected character, inspects meshes, facial object candidates,
head/leg-related vertex groups and rig data, then writes a JSON report.

Run from the backend folder:
blender.exe --background --python app\providers\aadwik_refinement_inspector.py -- --source "generated\aadwik_character_master_v4_sportsuit_fix.blend" --report "generated\reports\aadwik_refinement_inspection.json"
"""
import bpy
import sys
import os
import json
from mathutils import Vector

DEFAULT_SOURCE = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v4_sportsuit_fix.blend"
DEFAULT_REPORT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\reports\aadwik_refinement_inspection.json"

def args_after_double_dash():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description="Non-destructive Aadwik character inspector")
    p.add_argument("--source", default=DEFAULT_SOURCE)
    p.add_argument("--report", default=DEFAULT_REPORT)
    return p.parse_args(argv)

def world_bounds(obj):
    pts = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    if not pts:
        return None
    return {
        "min": [round(min(p[i] for p in pts), 5) for i in range(3)],
        "max": [round(max(p[i] for p in pts), 5) for i in range(3)],
        "dimensions": [round(max(p[i] for p in pts) - min(p[i] for p in pts), 5) for i in range(3)],
    }

def main():
    args = args_after_double_dash()
    source = os.path.abspath(args.source)
    report_path = os.path.abspath(args.report)

    if not os.path.isfile(source):
        raise FileNotFoundError("Source character .blend not found: " + source)

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=source)

    rig = bpy.data.objects.get("Aadwik_Main_Rig")
    if rig is None:
        rigs = [o for o in bpy.data.objects if o.type == "ARMATURE"]
        rig = rigs[0] if len(rigs) == 1 else None

    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    face_words = ("eye", "eyeball", "iris", "pupil", "brow", "lash", "nose", "mouth", "lip", "teeth", "tongue", "face", "head")
    leg_words = ("thigh", "shin", "calf", "leg", "knee", "foot", "toe")

    mesh_report = []
    facial_candidates = []
    leg_group_counts = {}

    for obj in meshes:
        names_lower = obj.name.lower()
        groups = [g.name for g in obj.vertex_groups]
        face_matches = [w for w in face_words if w in names_lower]
        leg_matches = [g for g in groups if any(w in g.lower() for w in leg_words)]
        item = {
            "name": obj.name,
            "vertices": len(obj.data.vertices),
            "polygons": len(obj.data.polygons),
            "bounds_world": world_bounds(obj),
            "parent": obj.parent.name if obj.parent else None,
            "armature_modifiers": [
                {"name": m.name, "object": m.object.name if m.object else None}
                for m in obj.modifiers if m.type == "ARMATURE"
            ],
            "materials": [m.name if m else None for m in obj.data.materials],
            "facial_name_matches": face_matches,
            "leg_vertex_groups": leg_matches,
        }
        mesh_report.append(item)
        if face_matches:
            facial_candidates.append({"object": obj.name, "matches": face_matches, "vertices": len(obj.data.vertices)})
        for group in leg_matches:
            leg_group_counts[group] = leg_group_counts.get(group, 0) + 1

    bone_report = []
    if rig:
        for bone in rig.data.bones:
            lower = bone.name.lower()
            if any(w in lower for w in ("head", "eye", "nose", "face", "thigh", "shin", "calf", "knee", "foot", "toe", "leg")):
                bone_report.append({
                    "name": bone.name,
                    "parent": bone.parent.name if bone.parent else None,
                    "use_deform": bool(bone.use_deform),
                    "head_local": [round(v, 5) for v in bone.head_local],
                    "tail_local": [round(v, 5) for v in bone.tail_local],
                })

    report = {
        "status": "inspection_complete",
        "source_blend": source,
        "source_modified": False,
        "rig": {
            "name": rig.name if rig else None,
            "bone_count": len(rig.data.bones) if rig else 0,
            "rig_id": rig.data.get("rig_id") if rig else None,
        },
        "mesh_count": len(meshes),
        "meshes": mesh_report,
        "facial_mesh_candidates": facial_candidates,
        "leg_vertex_group_object_counts": leg_group_counts,
        "relevant_bones": bone_report,
        "next_step": "Use these measured bounds and names to create a separate refinement copy. No geometry was changed by this script."
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("[AADWIK REFINEMENT] Inspection complete.", flush=True)
    print("[AADWIK REFINEMENT] Source was not modified.", flush=True)
    print("[AADWIK REFINEMENT] Meshes:", len(meshes), flush=True)
    print("[AADWIK REFINEMENT] Rig:", rig.name if rig else "NOT FOUND", flush=True)
    print("[AADWIK REFINEMENT] Report:", report_path, flush=True)

if __name__ == "__main__":
    main()
