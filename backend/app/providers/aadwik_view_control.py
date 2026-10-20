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

classes = (VIEW3D_OT_aadwik_set_view, VIEW3D_PT_aadwik_view_control)
def register():
    for cls in classes:
        try: bpy.utils.register_class(cls)
        except ValueError: pass
def unregister():
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except RuntimeError: pass
if __name__ == "__main__":
    register()
    print("Aadwik View Control enabled. In the 3D Viewport press N and open Aadwik.")
