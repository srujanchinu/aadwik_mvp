import bpy, math
from mathutils import Vector

SRC=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_base_v1.blend"
OUT_BLEND=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_base_v1_HAIR_V4.blend"
OUT_PNG=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_base_v1_HAIR_V4.png"

bpy.ops.wm.open_mainfile(filepath=SRC)

# Remove only prior Aadwik hair-test objects/lights.
for o in list(bpy.data.objects):
    if o.name.startswith("AADWIK_HAIR_V4"):
        bpy.data.objects.remove(o,do_unlink=True)

human=bpy.data.objects.get("Human")
if human is None: raise RuntimeError("Human mesh not found")

corners=[human.matrix_world @ Vector(c) for c in human.bound_box]
lo=min(v.z for v in corners); hi=max(v.z for v in corners)
H=hi-lo; C=sum(corners,Vector())/8
head=Vector((C.x,C.y,lo+H*0.855))

# Hair material: dark brown, non-metallic, moderately rough.
mat=bpy.data.materials.new("AADWIK_HAIR_V4_MAT")
mat.diffuse_color=(0.045,0.009,0.003,1)
mat.roughness=0.55
mat.metallic=0.0

# Compact crown cap, ending above ears instead of covering face.
rx,ry,rz=H*.062,H*.057,H*.070
verts=[]; faces=[]; rings=10; seg=64
for r in range(rings+1):
    phi=(math.pi/2)*(r/rings)
    rad=math.sin(phi); z=math.cos(phi)*rz
    for s in range(seg):
        a=2*math.pi*s/seg
        verts.append((head.x+rx*rad*math.cos(a),
                      head.y+ry*rad*math.sin(a),
                      head.z+z))
for r in range(rings):
    for s in range(seg):
        a=r*seg+s;b=r*seg+(s+1)%seg;c=(r+1)*seg+(s+1)%seg;d=(r+1)*seg+s
        faces.append((a,b,c,d))
me=bpy.data.meshes.new("AADWIK_HAIR_V4_CAP_MESH")
me.from_pydata(verts,[],faces);me.update()
cap=bpy.data.objects.new("AADWIK_HAIR_V4_CAP",me)
bpy.context.collection.objects.link(cap);cap.data.materials.append(mat)
bev=cap.modifiers.new("Hair Smooth","BEVEL");bev.width=H*.003;bev.segments=3

def lock(name,pts,r):
    cu=bpy.data.curves.new(name+"_CURVE","CURVE");cu.dimensions="3D"
    cu.resolution_u=8;cu.bevel_depth=r;cu.bevel_resolution=5
    sp=cu.splines.new("BEZIER");sp.bezier_points.add(len(pts)-1)
    for bp,p in zip(sp.bezier_points,pts):
        bp.co=p;bp.handle_left_type="AUTO";bp.handle_right_type="AUTO"
    o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(mat)

r=H*.008

# Short front fringe.
for i in range(7):
    t=(i-3)/3
    x=head.x+t*rx*.85
    lock(f"AADWIK_HAIR_V4_FRINGE_{i}",[
        (x,head.y-ry*.92,head.z+rz*.72),
        (x+t*rx*.06,head.y-ry*.96,head.z+rz*.42),
        (x+t*rx*.08,head.y-ry*.93,head.z+rz*.18)],r)

# Side locks hugging head.
for side in (-1,1):
    for i in range(3):
        x=head.x+side*rx*(.70+.07*i)
        lock(f"AADWIK_HAIR_V4_SIDE_{side}_{i}",[
            (x,head.y-ry*.15,head.z+rz*.58),
            (x+side*rx*.05,head.y-ry*.05,head.z+rz*.12),
            (x+side*rx*.03,head.y+ry*.02,head.z-rz*(.30+.12*i))],r)

# Back hair, short and clearly separated into locks.
for i in range(9):
    t=(i-4)/4
    x=head.x+t*rx*.9
    lock(f"AADWIK_HAIR_V4_BACK_{i}",[
        (x,head.y+ry*.88,head.z+rz*.58),
        (x,head.y+ry*.95,head.z+rz*.20),
        (x+t*rx*.05,head.y+ry*1.00,head.z-rz*.45)],r*1.15)

# Camera.
scene=bpy.context.scene
cam=scene.camera
target=Vector((C.x,C.y,lo+H*.52))
cam.location=Vector((C.x+H*1.55,C.y-H*2.65,lo+H*.70))
cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.lens=60

# Neutral lighting so hair and body are both readable.
world=scene.world
if world is None:
    world=bpy.data.worlds.new("World");scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.035,.035,.035,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.45

for o in list(bpy.data.objects):
    if o.name.startswith("AADWIK_HAIR_V4_LIGHT"): bpy.data.objects.remove(o,do_unlink=True)

def area(name,loc,energy,size):
    d=bpy.data.lights.new(name,"AREA");d.energy=energy;d.shape="DISK";d.size=size
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc
    o.rotation_euler=(target-o.location).to_track_quat("-Z","Y").to_euler()
area("AADWIK_HAIR_V4_LIGHT_KEY",(C.x-H*1.0,C.y-H*1.5,lo+H*1.25),500,H*.65)
area("AADWIK_HAIR_V4_LIGHT_FILL",(C.x+H*.9,C.y-H*.6,lo+H*.9),300,H*.8)

scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.render.filepath=OUT_PNG

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
bpy.ops.render.render(write_still=True)
print("[AADWIK HAIR V4] COMPLETE")
print("[AADWIK HAIR V4] BLEND:",OUT_BLEND)
print("[AADWIK HAIR V4] PREVIEW:",OUT_PNG)
