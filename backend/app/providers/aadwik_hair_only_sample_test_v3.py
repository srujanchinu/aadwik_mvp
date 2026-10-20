import bpy, math
from mathutils import Vector

SRC = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_base_v1.blend"
OUT_BLEND = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_base_v1_HAIR_V3.blend"
OUT_PNG = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_base_v1_HAIR_V3.png"

bpy.ops.wm.open_mainfile(filepath=SRC)

for obj in list(bpy.data.objects):
    if obj.name.startswith("AADWIK_HAIR_V3"):
        bpy.data.objects.remove(obj, do_unlink=True)

human = bpy.data.objects.get("Human")
if human is None:
    raise RuntimeError("Human mesh not found")

corners = [human.matrix_world @ Vector(c) for c in human.bound_box]
min_z = min(v.z for v in corners)
max_z = max(v.z for v in corners)
height = max_z - min_z
center = sum(corners, Vector()) / 8.0

# Estimate head center from upper body.
head_center = Vector((center.x, center.y, min_z + height * 0.855))
rx, ry, rz = height*0.068, height*0.062, height*0.074

hair = bpy.data.materials.new("AADWIK_HAIR_V3_MATERIAL")
hair.diffuse_color = (0.055, 0.012, 0.004, 1)
hair.metallic = 0.0
hair.roughness = 0.38

# Rounded cap covering the crown and upper sides.
verts=[]; faces=[]
rings=12; seg=64
for r in range(rings+1):
    phi=(math.pi/2)*(r/rings)
    radial=math.sin(phi)
    z=math.cos(phi)*rz
    for s in range(seg):
        a=2*math.pi*s/seg
        # Slightly fuller at sides/back.
        verts.append((head_center.x+rx*1.03*radial*math.cos(a),
                      head_center.y+ry*1.03*radial*math.sin(a),
                      head_center.z+z))
for r in range(rings):
    for s in range(seg):
        a=r*seg+s; b=r*seg+(s+1)%seg
        c=(r+1)*seg+(s+1)%seg; d=(r+1)*seg+s
        faces.append((a,b,c,d))
me=bpy.data.meshes.new("AADWIK_HAIR_V3_CAP_MESH")
me.from_pydata(verts,[],faces); me.update()
cap=bpy.data.objects.new("AADWIK_HAIR_V3_CAP",me)
bpy.context.collection.objects.link(cap); cap.data.materials.append(hair)

bev=cap.modifiers.new("Smooth Hair","BEVEL")
bev.width=height*0.005; bev.segments=3

def lock(name, pts, radius):
    cu=bpy.data.curves.new(name+"_CURVE","CURVE")
    cu.dimensions="3D"; cu.resolution_u=8
    cu.bevel_depth=radius; cu.bevel_resolution=5
    sp=cu.splines.new("BEZIER"); sp.bezier_points.add(len(pts)-1)
    for bp,p in zip(sp.bezier_points,pts):
        bp.co=p; bp.handle_left_type="AUTO"; bp.handle_right_type="AUTO"
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob); ob.data.materials.append(hair)
    return ob

r=height*0.013

# Front fringe: visible locks following forehead.
for i in range(7):
    t=(i-3)/3
    x=head_center.x + t*rx*0.78
    y=head_center.y - ry*0.92
    lock(f"AADWIK_HAIR_V3_FRINGE_{i}",[
        (x, y, head_center.z+rz*0.62),
        (x+t*rx*0.05, y-ry*0.06, head_center.z+rz*0.36),
        (x+t*rx*0.08, y-ry*0.03, head_center.z+rz*0.08)
    ],r*0.85)

# Side locks.
for side in (-1,1):
    for i in range(2):
        x=head_center.x+side*rx*(0.72+0.08*i)
        lock(f"AADWIK_HAIR_V3_SIDE_{side}_{i}",[
            (x,head_center.y-ry*0.20,head_center.z+rz*0.55),
            (x+side*rx*0.05,head_center.y-ry*0.18,head_center.z+rz*0.15),
            (x+side*rx*0.03,head_center.y-ry*0.08,head_center.z-rz*0.55)
        ],r)

# Back locks.
for i in range(9):
    t=(i-4)/4
    x=head_center.x+t*rx*0.82
    y=head_center.y+ry*0.82
    lock(f"AADWIK_HAIR_V3_BACK_{i}",[
        (x,y,head_center.z+rz*0.58),
        (x, y+ry*0.08, head_center.z+rz*0.05),
        (x+t*rx*0.04, y+ry*0.12, head_center.z-rz*0.95)
    ],r*1.12)

# Auto camera and brighter neutral lighting.
scene=bpy.context.scene
cam=scene.camera
target=Vector((center.x,center.y,min_z+height*0.53))
cam.location=Vector((center.x+height*1.55,center.y-height*2.55,min_z+height*0.72))
cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.lens=62

world=scene.world
if world is None:
    world=bpy.data.worlds.new("World"); scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.07,0.07,0.07,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.65

# Add simple key/fill lights for hair visibility.
for n in ["AADWIK_HAIR_V3_KEY","AADWIK_HAIR_V3_FILL"]:
    old=bpy.data.objects.get(n)
    if old: bpy.data.objects.remove(old,do_unlink=True)

def light(name, loc, energy, size):
    data=bpy.data.lights.new(name,"AREA"); data.energy=energy; data.shape="DISK"; data.size=size
    ob=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(ob); ob.location=loc
    ob.rotation_euler=(target-ob.location).to_track_quat("-Z","Y").to_euler()
    return ob
light("AADWIK_HAIR_V3_KEY",(center.x-height*1.1,center.y-height*1.3,min_z+height*1.25),850,height*0.55)
light("AADWIK_HAIR_V3_FILL",(center.x+height*1.0,center.y-height*0.5,min_z+height*0.95),500,height*0.7)

scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=640; scene.render.resolution_y=640; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"; scene.render.filepath=OUT_PNG

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
bpy.ops.render.render(write_still=True)

print("[AADWIK HAIR V3] COMPLETE")
print("[AADWIK HAIR V3] BLEND:",OUT_BLEND)
print("[AADWIK HAIR V3] PREVIEW:",OUT_PNG)
