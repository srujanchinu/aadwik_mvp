bl_info = {
    "name": "Aadwik View Control",
    "author": "Aadwik",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Aadwik",
    "description": "Quick viewport views and safe character framing",
    "category": "3D View",
}
import bpy
from mathutils import Euler, Vector

def target_object(context):
    obj = bpy.data.objects.get("Human")
    if obj and obj.type == 'MESH':
        return obj
    active = context.active_object
    if active and active.type in {'MESH', 'ARMATURE'}:
        return active
    return next((o for o in bpy.data.objects if o.type == 'MESH' and "human" in o.name.lower()), None)

def bbox_center(obj):
    return sum((obj.matrix_world @ Vector(c) for c in obj.bound_box), Vector()) / 8.0

class VIEW3D_OT_aadwik_set_view(bpy.types.Operator):
    bl_idname = "view3d.aadwik_set_view"
    bl_label = "Set Aadwik View"
    view: bpy.props.EnumProperty(items=[
        ('FRONT', "Front", ""), ('SIDE', "Side", ""), ('BACK', "Back", ""),
        ('THREE_QUARTER', "Three-quarter", ""), ('FACE', "Face close-up", ""),
        ('FULL', "Full body", "")
    ])
    def execute(self, context):
        if not context.area or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Run from a 3D Viewport")
            return {'CANCELLED'}
        rv3d = context.area.spaces.active.region_3d
        obj = target_object(context)
        if not obj:
            self.report({'WARNING'}, "Select the character mesh and retry")
            return {'CANCELLED'}
        center = bbox_center(obj)
        height = max(float(obj.dimensions.z), 1.0)
        face = center.copy()
        face.z += height * 0.27
        views = {
            'FRONT': (Euler((1.5707963, 0, 0), 'XYZ').to_quaternion(), center, height * 2.1, 'ORTHO'),
            'SIDE': (Euler((1.5707963, 0, 1.5707963), 'XYZ').to_quaternion(), center, height * 2.1, 'ORTHO'),
            'BACK': (Euler((1.5707963, 0, 3.1415927), 'XYZ').to_quaternion(), center, height * 2.1, 'ORTHO'),
            'THREE_QUARTER': (Euler((1.20, 0, 0.72), 'XYZ').to_quaternion(), center, height * 2.1, 'PERSP'),
            'FACE': (Euler((1.5707963, 0, 0), 'XYZ').to_quaternion(), face, max(height * 0.48, 0.5), 'PERSP'),
            'FULL': (Euler((1.20, 0, 0.72), 'XYZ').to_quaternion(), center, height * 2.3, 'ORTHO'),
        }
        rotation, location, distance, perspective = views[self.view]
        rv3d.view_rotation = rotation
        rv3d.view_location = location
        rv3d.view_distance = distance
        rv3d.view_perspective = perspective
        context.area.tag_redraw()
        return {'FINISHED'}



class VIEW3D_OT_aadwik_character_check(bpy.types.Operator):
    bl_idname = "view3d.aadwik_character_check"
    bl_label = "Run Character Check"
    bl_description = "Read-only checks for expected character objects, materials, and rig"
    bl_options = {'REGISTER'}

    def execute(self, context):
        objects = list(bpy.data.objects)
        names = {obj.name for obj in objects}
        mesh_objects = [obj for obj in objects if obj.type == 'MESH']

        def find_named_or_keyword(exact_names, keywords):
            for name in exact_names:
                if name in names:
                    return name
            matches = [obj.name for obj in mesh_objects
                       if any(word in obj.name.lower() for word in keywords)]
            return ", ".join(matches) if matches else "NOT FOUND"

        body = "Human" if "Human" in names else find_named_or_keyword([], ["human"])
        eyes = find_named_or_keyword(
            ["Human.high-p", "Human.low-p"], ["high-p", "low-p", "eye", "iris", "pupil"]
        )
        brows = find_named_or_keyword([], ["eyebrow", "brow"])
        hair = find_named_or_keyword([], ["hair", "afro", "bob", "short", "ponytail"])
        rig = "Aadwik_Main_Rig" if "Aadwik_Main_Rig" in names else find_named_or_keyword([], ["rig"])

        no_material = [obj.name for obj in mesh_objects if len(obj.data.materials) == 0]
        empty_slots = [obj.name for obj in mesh_objects
                       if len(obj.data.materials) > 0 and all(mat is None for mat in obj.data.materials)]

        report_lines = [
            "AADWIK CHARACTER CHECK (READ-ONLY)",
            "=================================",
            f"Body mesh: {body}",
            f"Eye-related mesh/object: {eyes}",
            f"Eyebrow-related mesh/object: {brows}",
            f"Hair-related mesh/object: {hair}",
            f"Rig: {rig}",
            "",
            f"Mesh objects with no material slots: {len(no_material)}",
        ]
        if no_material:
            report_lines.append("  " + ", ".join(no_material[:20]))
        report_lines.append(f"Mesh objects with empty material slots: {len(empty_slots)}")
        if empty_slots:
            report_lines.append("  " + ", ".join(empty_slots[:20]))
        report_lines += [
            "",
            "NOTE: Object presence/material slots do not prove that eyes render correctly.",
            "No scene objects, materials, weights, or rig data were changed."
        ]

        report = "\n".join(report_lines)
        print("\n" + report + "\n")
        self.report({'INFO'}, "Character check printed to Blender System Console")
        return {'FINISHED'}



class VIEW3D_OT_aadwik_visual_audit(bpy.types.Operator):
    bl_idname = "view3d.aadwik_visual_audit"
    bl_label = "Run Visual Quality Audit"
    bl_description = "Read-only audit of character parts and material slots"
    bl_options = {'REGISTER'}

    def execute(self, context):
        objects = list(bpy.data.objects)
        names = {obj.name for obj in objects}
        meshes = [obj for obj in objects if obj.type == 'MESH']

        def match(exact, keywords):
            for name in exact:
                if name in names:
                    return name
            found = [obj.name for obj in meshes if any(k in obj.name.lower() for k in keywords)]
            return ", ".join(found[:8]) if found else "NOT FOUND"

        lines = [
            "AADWIK VISUAL QUALITY AUDIT (READ-ONLY)",
            "=======================================",
            f"Body: {'Human' if 'Human' in names else match([], ['human'])}",
            f"Eyes: {match(['Human.high-p', 'Human.low-p'], ['eye', 'high-p', 'low-p'])}",
            f"Eyebrows: {match(['Human.eyebrow001'], ['eyebrow'])}",
            f"Hair: {match(['Human.ponytail01'], ['ponytail', 'hair', 'afro', 'bob', 'short'])}",
            f"Rig: {'Aadwik_Main_Rig' if 'Aadwik_Main_Rig' in names else match([], ['aadwik_main_rig'])}",
            "",
            "MATERIAL SLOTS ON LIKELY CHARACTER MESHES:",
        ]
        core = [obj for obj in meshes if obj.name.lower() == "human" or
                any(k in obj.name.lower() for k in ("high-p", "low-p", "eyebrow", "ponytail", "hair", "afro", "bob", "short"))]
        if not core:
            core = [obj for obj in meshes if "human" in obj.name.lower()]
        if core:
            for obj in core:
                slots = list(obj.data.materials)
                assigned = sum(1 for mat in slots if mat is not None)
                status = f"{assigned}/{len(slots)} assigned" if slots else "NO MATERIAL SLOTS"
                lines.append(f"- {obj.name}: {status}")
        else:
            lines.append("- No likely character meshes identified.")
        lines += [
            "",
            "This checks object presence and material slots, not visual quality itself.",
            "No objects, materials, weights, or rig data were changed.",
        ]
        report = "\n".join(lines)
        block = bpy.data.texts.get("AADWIK_VISUAL_AUDIT_REPORT") or bpy.data.texts.new("AADWIK_VISUAL_AUDIT_REPORT")
        block.clear()
        block.write(report)
        print("\n" + report + "\n")
        self.report({'INFO'}, "Report saved in Text datablock: AADWIK_VISUAL_AUDIT_REPORT")
        return {'FINISHED'}


class VIEW3D_PT_aadwik_view_control(bpy.types.Panel):
    bl_label = "Aadwik View Control"
    bl_idname = "VIEW3D_PT_aadwik_view_control"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Aadwik"
    def draw(self, context):
        layout = self.layout
        layout.label(text="Character View")
        grid = layout.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True, align=True)
        for label, view in [
            ("Front", 'FRONT'), ("Side", 'SIDE'), ("Back", 'BACK'),
            ("3/4 View", 'THREE_QUARTER'), ("Face Close-up", 'FACE'), ("Full Body", 'FULL')
        ]:
            op = grid.operator("view3d.aadwik_set_view", text=label)
            op.view = view
        layout.separator()
        layout.label(text="View controls only; mesh and rig untouched.")
        layout.operator("wm.save_mainfile", text="Save Current File", icon='FILE_TICK')
        layout.operator("view3d.aadwik_character_check", text="Run Character Check", icon='CHECKMARK')

classes = (VIEW3D_OT_aadwik_set_view, VIEW3D_OT_aadwik_character_check, VIEW3D_OT_aadwik_visual_audit, VIEW3D_PT_aadwik_view_control)
def register():
    # Replace any earlier version of these classes when the script is run again.
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except (RuntimeError, ValueError):
            pass
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except (RuntimeError, ValueError):
            pass
if __name__ == "__main__":
    register()
    print("Aadwik View Control enabled. In the 3D Viewport press N and open Aadwik.")
