bl_info = {
    "name": "Aadwik Quick Animation Starter",
    "author": "Aadwik",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "3D View > Sidebar > Aadwik Anim",
    "description": "Creates a separate, subtle idle-test action on recognized Rigify controls",
    "category": "Animation",
}

import bpy
from math import radians

RIG_NAME = "Aadwik_Main_Rig"

def find_control(pose_bones, tokens):
    excluded = ("def-", "mch-", "org-", "wgt-", "tweak", "socket")
    candidates = []
    for pb in pose_bones:
        n = pb.name.lower()
        if any(x in n for x in excluded):
            continue
        if any(token in n for token in tokens):
            candidates.append(pb)
    # Prefer exact semantic control names and avoid FK/IK duplicates when possible.
    candidates.sort(key=lambda pb: (
        0 if pb.name.lower().startswith(("head", "chest", "spine")) else 1,
        len(pb.name)
    ))
    return candidates[0] if candidates else None

class VIEW3D_OT_aadwik_make_idle_test(bpy.types.Operator):
    bl_idname = "view3d.aadwik_make_idle_test"
    bl_label = "Create 2-Second Idle Test"
    bl_description = "Creates a new action with subtle head/torso motion; does not overwrite existing actions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = bpy.data.objects.get(RIG_NAME)
        if not rig or rig.type != 'ARMATURE':
            self.report({'ERROR'}, f"Rig '{RIG_NAME}' not found")
            return {'CANCELLED'}

        # Only use obvious user-facing controls, never DEF/MCH/ORG mechanism bones.
        head = find_control(rig.pose.bones, ("head",))
        torso = find_control(rig.pose.bones, ("chest", "spine"))
        chosen = [pb for pb in (torso, head) if pb]
        if not chosen:
            self.report({'ERROR'}, "No obvious head/chest/spine control bones found; no animation created")
            return {'CANCELLED'}

        scene = context.scene
        old_frame = scene.frame_current
        old_action = rig.animation_data.action if rig.animation_data else None

        if not rig.animation_data:
            rig.animation_data_create()

        base_action_name = "AADWIK_Idle_Test_v1"
        action_name = base_action_name
        suffix = 2
        while bpy.data.actions.get(action_name):
            action_name = f"{base_action_name}_{suffix}"
            suffix += 1
        action = bpy.data.actions.new(action_name)
        rig.animation_data.action = action

        # Use a short 2-second loop at 24 fps (frames 1–49).
        scene.render.fps = max(scene.render.fps, 24)
        scene.frame_start = 1
        scene.frame_end = 49
        keys = (1, 13, 25, 37, 49)

        for pb in chosen:
            pb.rotation_mode = 'XYZ'
            base = pb.rotation_euler.copy()
            # Very subtle motion; head turns slightly, torso gently breathes.
            if pb == head:
                delta = radians(3.0)
                axis = 2
            else:
                delta = radians(1.0)
                axis = 0
            for idx, frame in enumerate(keys):
                # Return to neutral at the loop boundary.
                amount = (0.0, 1.0, 0.0, -1.0, 0.0)[idx]
                pb.rotation_euler = base.copy()
                pb.rotation_euler[axis] += delta * amount
                pb.keyframe_insert(data_path="rotation_euler", frame=frame, group=pb.name)
            pb.rotation_euler = base

        scene.frame_set(1)
        scene.frame_current = old_frame if old_frame >= scene.frame_start and old_frame <= scene.frame_end else 1
        context.view_layer.update()

        print("\\nAADWIK QUICK ANIMATION STARTER")
        print("Created new action:", action.name)
        print("Rig:", rig.name)
        print("Animated controls:", ", ".join(pb.name for pb in chosen))
        print("Frames: 1–49 at current scene FPS; inspect by pressing Spacebar in the timeline.")
        print("Existing actions were not deleted; the new action is assigned to the rig.")
        self.report({'INFO'}, "Idle test action created. Press Spacebar over the Timeline to preview.")
        return {'FINISHED'}

class VIEW3D_PT_aadwik_anim_panel(bpy.types.Panel):
    bl_label = "Aadwik Animation"
    bl_idname = "VIEW3D_PT_aadwik_anim_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Aadwik Anim"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Animation Starter")
        layout.operator("view3d.aadwik_make_idle_test", text="Create 2-Second Idle Test", icon='ANIM')
        layout.label(text="Creates a new action; inspect before saving.")

classes = (VIEW3D_OT_aadwik_make_idle_test, VIEW3D_PT_aadwik_anim_panel)

def register():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass

if __name__ == "__main__":
    register()
    print("Aadwik Quick Animation Starter ready. In the 3D Viewport press N and open 'Aadwik Anim'.")
