import bpy
from mathutils import Vector
import math
from pathlib import Path

target = bpy.data.objects.get("Human")
camera = bpy.context.scene.camera
if not target or not camera:
    raise RuntimeError("Human or Camera not found")

corners = [target.matrix_world @ Vector(c) for c in target.bound_box]
mn = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
mx = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
center = (mn + mx) * 0.5
height = max(mx.z - mn.z, 0.1)

forward = camera.matrix_world.to_quaternion() @ Vector((0,0,-1))
forward.z = 0
if forward.length < 0.01:
    forward = Vector((0,-1,0))
forward.normalize()

fov = 2 * math.atan(18.0 / (2 * camera.data.lens))

# V2: closer framing, targeting about 75% of image height.
distance = max((height * 0.36) / math.tan(fov/2), height * 1.0)

aim = center + Vector((0,0,height*0.04))
camera.location = aim - forward * distance
camera.rotation_euler = (aim-camera.location).to_track_quat("-Z","Y").to_euler()

scene = bpy.context.scene
scene.camera = camera
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100

src = Path(bpy.data.filepath)
out_blend = src.with_name(src.stem + "_V2.blend")
out_png = src.with_name(src.stem + "_V2.png")

bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
scene.render.filepath = str(out_png)
bpy.ops.render.render(write_still=True)

print("[AADWIK CAMERA AUTO V2] COMPLETE")
print("[AADWIK CAMERA AUTO V2] BLEND:", out_blend)
print("[AADWIK CAMERA AUTO V2] PREVIEW:", out_png)
