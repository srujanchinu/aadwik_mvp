import bpy, math
from mathutils import Vector
from pathlib import Path

human = bpy.data.objects.get("Human")
camera = bpy.context.scene.camera
if human is None or camera is None:
    raise RuntimeError("Human or Camera not found")

for o in list(bpy.data.objects):
    if o.name.startswith("AADWIK_SAMPLE_"):
        bpy.data.objects.remove(o, do_unlink=True)

def material(name, color):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.roughness = 0.55
    return m

hair_mat = material("AADWIK_SAMPLE_HAIR", (0.07,0.025,0.012))
blue = material("AADWIK_SAMPLE_CLOTH_BLUE", (0.06,0.28,0.65))
light = material("AADWIK_SAMPLE_CLOTH_LIGHT", (0.15,0.55,0.9))

corners = [human.matrix_world @ Vector(c) for c in human.bound_box]
mn = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
mx = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
center = (mn+mx)*0.5
h = max(mx.z-mn.z, 0.1)
w = max(mx.x-mn.x, 0.1)
d = max(mx.y-mn.y, 0.1)

# Hair cap
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(center.x, center.y, mn.z+h*0.87))
hair=bpy.context.object
hair.name="AADWIK_SAMPLE_HAIR_CAP"
hair.scale=(w*0.17,d*0.19,h*0.105)
hair.data.materials.append(hair_mat)
bpy.ops.object.shade_smooth()

# Hair back
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(center.x, center.y+d*0.07, mn.z+h*0.835))
back=bpy.context.object
back.name="AADWIK_SAMPLE_HAIR_BACK"
back.scale=(w*0.15,d*0.18,h*0.14)
back.data.materials.append(hair_mat)
bpy.ops.object.shade_smooth()

# Clothing top
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(center.x,center.y,mn.z+h*0.62))
top=bpy.context.object
top.name="AADWIK_SAMPLE_CLOTHING_TOP"
top.scale=(w*0.24,d*0.30,h*0.17)
top.data.materials.append(light)
bpy.ops.object.shade_smooth()

# Simple dress
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=w*0.34, radius2=w*0.20, depth=h*0.32, location=(center.x,center.y,mn.z+h*0.43))
dress=bpy.context.object
dress.name="AADWIK_SAMPLE_CLOTHING_DRESS"
dress.data.materials.append(blue)
bpy.ops.object.shade_smooth()

# Camera framing
forward=camera.matrix_world.to_quaternion() @ Vector((0,0,-1))
forward.z=0
if forward.length<0.01: forward=Vector((0,-1,0))
forward.normalize()
fov=2*math.atan(18/(2*camera.data.lens))
distance=max((h*0.36)/math.tan(fov/2),h)
aim=center+Vector((0,0,h*0.04))
camera.location=aim-forward*distance
camera.rotation_euler=(aim-camera.location).to_track_quat("-Z","Y").to_euler()

scene=bpy.context.scene
scene.camera=camera
scene.render.resolution_x=640
scene.render.resolution_y=640
scene.render.resolution_percentage=100

src=Path(bpy.data.filepath)
out_blend=src.with_name(src.stem+"_HAIR_CLOTHING_TEST.blend")
out_png=src.with_name(src.stem+"_HAIR_CLOTHING_TEST.png")
bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
scene.render.filepath=str(out_png)
bpy.ops.render.render(write_still=True)

print("[AADWIK SAMPLE] COMPLETE")
print("[AADWIK SAMPLE] BLEND:",out_blend)
print("[AADWIK SAMPLE] PREVIEW:",out_png)
