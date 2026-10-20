import bpy
import math
from mathutils import Vector

s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.render.resolution_x = 960
s.render.resolution_y = 540
s.render.resolution_percentage = 100
s.view_settings.view_transform = 'AgX'

objs = [o for o in s.objects if o.type == 'MESH']
if not objs:
    raise RuntimeError("No mesh assets found in this blend file")

pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
center = (lo + hi) / 2
d = max((hi - lo).length, 5)

camdata = bpy.data.cameras.new('TEMP_PreviewCamera')
cam = bpy.data.objects.new('TEMP_PreviewCamera', camdata)
s.collection.objects.link(cam)
cam.location = center + Vector((d * 1.5, -d * 2, d * 1.1))
cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
camdata.lens = 50
s.camera = cam

ld = bpy.data.lights.new('TEMP_Sun', 'SUN')
ld.energy = 2.0
light = bpy.data.objects.new('TEMP_Sun', ld)
s.collection.objects.link(light)
light.rotation_euler = (math.radians(25), math.radians(-20), math.radians(-25))

ad = bpy.data.lights.new('TEMP_Fill', 'AREA')
ad.energy = 1800
ad.shape = 'DISK'
ad.size = d
area = bpy.data.objects.new('TEMP_Fill', ad)
s.collection.objects.link(area)
area.location = center + Vector((0, -d, d))
area.rotation_euler = (center - area.location).to_track_quat('-Z', 'Y').to_euler()

if s.world:
    s.world.color = (0.18, 0.18, 0.18)

s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\step8d_assets_preview.png'
bpy.ops.render.render(write_still=True)
print("PREVIEW SAVED:", s.render.filepath)
print("MESH COUNT:", len(objs))
print("SCENE BOUNDS:", tuple(round(v, 2) for v in (hi - lo)))
