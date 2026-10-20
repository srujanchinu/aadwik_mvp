import bpy, os, json
SOURCE=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3.blend"
OUT=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v4_legfix.blend"
REPORT=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\reports\aadwik_legfix_v4_report.json"
RIG="Aadwik_Main_Rig"; BODY="Human"; IK="foot_ik.L"; Z=.09
ZMIN=.45; ZMAX=.95
bpy.ops.wm.open_mainfile(filepath=SOURCE)
rig=bpy.data.objects[RIG]; body=bpy.data.objects[BODY]
bpy.context.view_layer.objects.active=rig
if rig.mode!="OBJECT": bpy.ops.object.mode_set(mode="OBJECT")
def reset():
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode="POSE")
    for b in rig.pose.bones:
        b.location=(0,0,0); b.rotation_mode="QUATERNION"; b.rotation_quaternion=(1,0,0,0); b.scale=(1,1,1)
    bpy.ops.object.mode_set(mode="OBJECT")
def pos():
    dg=bpy.context.evaluated_depsgraph_get(); e=body.evaluated_get(dg); m=e.to_mesh()
    try:return [v.co.copy() for v in m.vertices]
    finally:e.to_mesh_clear()
reset(); neutral=pos()
rig.pose.bones[IK].location.z=Z; bpy.context.view_layer.update(); posed=pos()
n=min(len(neutral),len(posed)); ds=[]
for i in range(n):
    if ZMIN<=neutral[i].z<=ZMAX: ds.append((i,(posed[i]-neutral[i]).length))
ds.sort(key=lambda x:x[1],reverse=True)
report={"source":SOURCE,"output":OUT,"pose":{"bone":IK,"z":Z},"region":[ZMIN,ZMAX],
"neutral_vertices":len(neutral),"posed_vertices":len(posed),
"avg_displacement":sum(x[1] for x in ds)/len(ds) if ds else 0,
"max_displacement":ds[0][1] if ds else 0,
"top_vertices":[{"index":i,"displacement":d} for i,d in ds[:25]],
"fix":"No automatic weight overwrite yet; diagnostic is saved first to prevent damaging the master."}
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,"w",encoding="utf-8").write(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
