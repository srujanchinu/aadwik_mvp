import bpy, os, sys, math, traceback
from pathlib import Path
from mathutils import Vector

print("[AADWIK RIGIFY V2] START")

def arg(name, default=None):
    a=sys.argv
    if "--" not in a: return default
    a=a[a.index("--")+1:]
    for i,x in enumerate(a):
        if x==name and i+1<len(a): return a[i+1]
    return default

SOURCE=arg("--source")
BLEND_OUT=arg("--blend_out", r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_rigify_v2.blend")
RENDER_OUT=arg("--render_out", r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_rigify_v2.png")
WIDTH=int(arg("--width","640")); HEIGHT=int(arg("--height","640"))

if not SOURCE or not os.path.isfile(SOURCE):
    raise RuntimeError("[AADWIK RIGIFY V2] V3 source not found: "+str(SOURCE))

import addon_utils
addon_utils.enable("rigify", default_set=False, persistent=False)
print("[AADWIK RIGIFY V2] Rigify enabled")

source_code=Path(SOURCE).read_text(encoding="utf-8")
g={"__name__":"__aadwik_maya_v3__","__file__":SOURCE,"__builtins__":__builtins__}
exec(compile(source_code,SOURCE,"exec"),g,g)
bpy.context.view_layer.update()

meshes=[o for o in bpy.context.scene.objects if o.type=="MESH" and not o.name.startswith(("AADWIK_RIGIFY_","WGT-","DEF-","ORG-","MCH-")) and o.name.lower() not in {"ground","floor"}]
if not meshes: raise RuntimeError("[AADWIK RIGIFY V2] No character meshes found.")
print("[AADWIK RIGIFY V2] Meshes:",len(meshes))

corners=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mn=Vector((min(v.x for v in corners),min(v.y for v in corners),min(v.z for v in corners)))
mx=Vector((max(v.x for v in corners),max(v.y for v in corners),max(v.z for v in corners)))
center=(mn+mx)*.5; height=mx.z-mn.z
for o in meshes:
    o.location.x-=center.x; o.location.y-=center.y; o.location.z-=mn.z
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name in {"metarig","rig"} or o.name.startswith(("AADWIK_MAYA_METARIG","AADWIK_MAYA_RIGIFY","rigify_rig")):
        bpy.data.objects.remove(o,do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
try:
    bpy.ops.armature.metarig_add()
except Exception as e:
    raise RuntimeError("[AADWIK RIGIFY V2] metarig_add failed: "+repr(e))

metarig=bpy.context.object
if not metarig or metarig.type!="ARMATURE":
    raise RuntimeError("[AADWIK RIGIFY V2] Metarig not created.")
metarig.name="AADWIK_MAYA_METARIG_V2"
if height>0.01:
    s=height/2.0
    metarig.scale=(s,s,s)
metarig.location=(0,0,0)
bpy.context.view_layer.update()
print("[AADWIK RIGIFY V2] Human metarig created")

out=Path(BLEND_OUT); out.parent.mkdir(parents=True,exist_ok=True)
checkpoint=out.with_name(out.stem+"_METARIG.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))
print("[AADWIK RIGIFY V2] METARIG CHECKPOINT:",checkpoint)

bpy.ops.object.select_all(action="DESELECT"); metarig.select_set(True); bpy.context.view_layer.objects.active=metarig
try:
    bpy.ops.pose.rigify_generate()
except Exception:
    print(traceback.format_exc())
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    raise RuntimeError("[AADWIK RIGIFY V2] Rigify generation failed.")

rigs=[o for o in bpy.context.scene.objects if o.type=="ARMATURE" and o!=metarig]
if not rigs: raise RuntimeError("[AADWIK RIGIFY V2] No generated rig found.")
rig=rigs[-1]; rig.name="AADWIK_MAYA_RIGIFY_V2"
print("[AADWIK RIGIFY V2] GENERATED RIG:",rig.name)

bpy.ops.object.select_all(action="DESELECT")
for o in meshes: o.select_set(True)
rig.select_set(True); bpy.context.view_layer.objects.active=rig
try:
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    print("[AADWIK RIGIFY V2] Automatic skinning completed")
except Exception as e:
    print("[AADWIK RIGIFY V2] Skinning warning:",repr(e))

pose=rig.pose.bones
for name,rot in [("head",(math.radians(-5),0,math.radians(-8))),("upper_arm_parent.L",(0,0,math.radians(-15))),("upper_arm_parent.R",(0,0,math.radians(15))),("hand.L",(0,0,math.radians(-8))),("hand.R",(0,0,math.radians(8)))]:
    b=pose.get(name)
    if b:
        b.rotation_mode="XYZ"; b.rotation_euler=rot; print("[AADWIK RIGIFY V2] POSE:",name)

scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=WIDTH; scene.render.resolution_y=HEIGHT; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"; scene.render.filepath=RENDER_OUT

for n in ["AADWIK_RIGIFY_V2_CAMERA","AADWIK_RIGIFY_V2_KEY","AADWIK_RIGIFY_V2_FILL","AADWIK_RIGIFY_V2_RIM","AADWIK_RIGIFY_V2_GROUND"]:
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o,do_unlink=True)

bpy.ops.mesh.primitive_plane_add(size=12,location=(0,0,0)); ground=bpy.context.object; ground.name="AADWIK_RIGIFY_V2_GROUND"
mat=bpy.data.materials.new("AADWIK_RIGIFY_V2_GROUND_MAT"); mat.diffuse_color=(.055,.065,.08,1); ground.data.materials.append(mat)

cd=bpy.data.cameras.new("AADWIK_RIGIFY_V2_CAMERA_DATA"); cam=bpy.data.objects.new("AADWIK_RIGIFY_V2_CAMERA",cd); bpy.context.collection.objects.link(cam)
cam.location=(0,-4.8,height*.53); cam.rotation_euler=(Vector((0,0,height*.5))-cam.location).to_track_quat("-Z","Y").to_euler(); cd.lens=55; scene.camera=cam

def light(name,loc,energy,size):
    ld=bpy.data.lights.new(name+"_DATA","AREA"); o=bpy.data.objects.new(name,ld); bpy.context.collection.objects.link(o)
    o.location=loc; ld.energy=energy; ld.shape="DISK"; ld.size=size
    o.rotation_euler=(Vector((0,0,height*.5))-o.location).to_track_quat("-Z","Y").to_euler()
for args in [("AADWIK_RIGIFY_V2_KEY",(-3,-4,5),900,3),("AADWIK_RIGIFY_V2_FILL",(3,-2,3),500,3),("AADWIK_RIGIFY_V2_RIM",(0,3,4),800,2)]: light(*args)

bpy.ops.wm.save_as_mainfile(filepath=str(out))
bpy.ops.render.render(write_still=True)
print("[AADWIK RIGIFY V2] BLEND:",out)
print("[AADWIK RIGIFY V2] PNG:",RENDER_OUT)
print("[AADWIK RIGIFY V2] COMPLETE")
