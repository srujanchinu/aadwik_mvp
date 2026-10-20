import bpy
from mathutils import Vector

scene = bpy.context.scene
cam = scene.camera
if cam is None:
    raise RuntimeError("No active camera found")

target = Vector((0, -0.10, 0.86))
cam.location = target + Vector((0, -2.0, 0.12))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 70
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.filepath = bpy.path.abspath("//aadwik_v16_face_preview.png")
bpy.ops.render.render(write_still=True)
print("SAVED:", scene.render.filepath)





