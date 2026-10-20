import bpy, math
from mathutils import Vector
from pathlib import Path

OUT=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_maya_v5.blend"
PREVIEW=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\maya_v5_preview.png"

print("[AADWIK MAYA V5 FIX] START - CONNECTED ORGANIC BODY")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(n,c,r=.4):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value=(*c,1)
        b.inputs["Roughness"].default_value=r
    return m

skin=mat("V5 Skin",(.56,.27,.13),.38)
light=mat("V5 Skin Light",(.68,.35,.18),.4)
dress=mat("V5 Dress",(.035,.15,.52),.34)
scarf=mat("V5 Scarf",(.02,.62,.82),.3)
hair=mat("V5 Hair",(.012,.008,.006),.27)
shoe=mat("V5 Shoe",(.02,.025,.055),.25)
white=mat("V5 Eye White",(.94,.96,1),.2)
iris=mat("V5 Iris",(.06,.36,.65),.18)
black=mat("V5 Pupil",(.002,.002,.003),.16)
mouth=mat("V5 Mouth",(.12,.008,.012),.3)

def uv(n,l,s,ma,seg=48,rings=28):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=l)
    o=bpy.context.object; o.name=n; o.scale=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(ma)
    for f in o.data.polygons:f.use_smooth=True
    return o

# Organic connected body using metaball field.
bpy.ops.object.metaball_add(type="BALL",location=(0,0,.95))
mb=bpy.context.object
mb.name="MAYA_V5_CONNECTED_BODY_FIELD"
meta=mb.data; meta.name="MAYA_V5_BODY_META"
meta.resolution=.055; meta.render_resolution=.035
meta.threshold=.58

def ball(p,r):
    e=meta.elements.new(); e.co=Vector(p); e.radius=r; return e

# torso/pelvis chain
for p,r in [
    ((0,0,.82),.48),((0,0,1.02),.52),((0,0,1.25),.47),
    ((0,0,1.48),.50),((0,0,1.70),.54),((0,0,1.84),.43),
    ((-.22,0,1.75),.34),((.22,0,1.75),.34),
    ((-.30,0,1.55),.29),((.30,0,1.55),.29),
    ((-.19,0,.92),.32),((.19,0,.92),.32)]:
    ball(p,r)

# arms and legs are part of the same field
for s in (-1,1):
    for p,r in [
        ((s*.47,0,1.73),.25),((s*.54,0,1.58),.22),
        ((s*.59,0,1.40),.19),((s*.60,0,1.22),.17),
        ((s*.60,0,1.07),.16),((s*.18,0,.72),.25),
        ((s*.18,0,.52),.20),((s*.18,0,.29),.17),
        ((s*.18,-.01,.12),.15)]:
        ball(p,r)

# convert metaball field to real mesh
bpy.context.view_layer.objects.active=mb
mb.select_set(True)
bpy.ops.object.convert(target="MESH")
body=bpy.context.object
body.name="MAYA_V5_CONNECTED_BODY"
body.data.materials.append(skin)

# smooth/subdivision
for f in body.data.polygons:f.use_smooth=True
sub=body.modifiers.new("V5_SUBDIVISION","SUBSURF"); sub.levels=1; sub.render_levels=2

# Head and neck, intentionally separate from body but shaped human-like.
uv("MAYA_V5_NECK",(0,0,2.04),(.16,.15,.17),skin)
uv("MAYA_V5_HEAD",(0,0,2.39),(.285,.235,.35),skin,64,40)
uv("MAYA_V5_JAW",(0,-.025,2.25),(.22,.19,.17),light,56,32)
uv("MAYA_V5_EAR_L",(-.275,0,2.40),(.045,.035,.09),light)
uv("MAYA_V5_EAR_R",(.275,0,2.40),(.045,.035,.09),light)

# Hair
uv("MAYA_V5_HAIR_CROWN",(0,.02,2.67),(.31,.25,.16),hair,64,32)
for s in (-1,1):
    uv(f"MAYA_V5_HAIR_SIDE_{s}",(s*.275,.02,2.44),(.065,.08,.29),hair,40,24)
for i,x in enumerate([-.22,-.14,-.06,.06,.14,.22]):
    uv(f"MAYA_V5_FRINGE_{i}",(x,-.18,2.64),(.07,.05,.10),hair,40,20)

# Face
for s,x in (("L",-.105),("R",.105)):
    uv("MAYA_V5_EYE_"+s,(x,-.225,2.48),(.073,.035,.083),white)
    uv("MAYA_V5_IRIS_"+s,(x,-.258,2.48),(.036,.012,.044),iris,40,20)
    uv("MAYA_V5_PUPIL_"+s,(x,-.269,2.48),(.015,.007,.020),black,32,16)
uv("MAYA_V5_NOSE",(0,-.25,2.37),(.045,.04,.07),light,40,20)
uv("MAYA_V5_MOUTH",(0,-.25,2.27),(.065,.012,.018),mouth,32,16)

# Clothing shell, fitted to body
def ring(n,rs,ma,seg=64):
    vs=[];fs=[]
    for z,rx,ry in rs:
        for i in range(seg):
            a=2*math.pi*i/seg;vs.append((rx*math.cos(a),ry*math.sin(a),z))
    for j in range(len(rs)-1):
        for i in range(seg):
            a=j*seg+i;b=j*seg+(i+1)%seg;c=(j+1)*seg+(i+1)%seg;d=(j+1)*seg+i
            fs.append((a,b,c,d))
    me=bpy.data.meshes.new(n+"_MESH");me.from_pydata(vs,[],fs);me.update()
    o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(ma)
    for f in me.polygons:f.use_smooth=True
    return o

ring("MAYA_V5_DRESS",[(.92,.36,.27),(1.15,.36,.255),(1.42,.41,.27),(1.68,.47,.30),(1.84,.45,.29)],dress)

# scarf
bpy.ops.mesh.primitive_torus_add(major_radius=.15,minor_radius=.035,major_segments=64,minor_segments=16,location=(0,-.01,2.05))
sc=bpy.context.object;sc.name="MAYA_V5_SCARF";sc.data.materials.append(scarf)
for f in sc.data.polygons:f.use_smooth=True
uv("MAYA_V5_SCARF_TAIL",(.17,-.05,1.87),(.055,.045,.22),scarf,40,20)

# Shoes
for s in (-1,1):
    uv(f"MAYA_V5_SHOE_{s}",(s*.18,-.16,.07),(.17,.29,.075),shoe)
    uv(f"MAYA_V5_SOLE_{s}",(s*.18,-.17,.025),(.18,.30,.035),shoe)

# Metadata
root=bpy.data.objects.new("MAYA_V5_CHARACTER_ROOT",None);bpy.context.collection.objects.link(root)
root["character_id"]="char_maya_v5";root["identity_locked"]=True;root["asset_version"]="V5"
root["geometry_type"]="organic_connected_metaball_mesh";root["rig_ready"]=False

# Ground/camera/lights
bpy.ops.mesh.primitive_plane_add(size=8,location=(0,0,0))
g=bpy.context.object;g.name="MAYA_V5_GROUND";g.data.materials.append(mat("V5 Ground",(.025,.032,.045),.75))
bpy.ops.object.camera_add(location=(0,-7,2));cam=bpy.context.object;bpy.context.scene.camera=cam
cam.rotation_euler=(Vector((0,0,1.35))-cam.location).to_track_quat("-Z","Y").to_euler();cam.data.lens=58
for n,loc,en,size in [("KEY",(-3,-4,4.5),1000,3),("FILL",(3,-2,3),550,2.5),("RIM",(0,2.5,4),850,2)]:
    bpy.ops.object.light_add(type="AREA",location=loc);l=bpy.context.object;l.name="V5_"+n;l.data.energy=en;l.data.shape="DISK";l.data.size=size
    l.rotation_euler=(Vector((0,0,1.5))-l.location).to_track_quat("-Z","Y").to_euler()

scn=bpy.context.scene;scn.render.engine="BLENDER_EEVEE";scn.render.resolution_x=640;scn.render.resolution_y=640;scn.render.resolution_percentage=100
scn.render.image_settings.file_format="PNG";scn.render.filepath=PREVIEW;scn.world.color=(.012,.018,.03)
Path(OUT).parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT);bpy.ops.render.render(write_still=True)
print("[AADWIK MAYA V5 FIX] SAVED:",OUT);print("[AADWIK MAYA V5 FIX] PREVIEW:",PREVIEW);print("[AADWIK MAYA V5 FIX] COMPLETE")
