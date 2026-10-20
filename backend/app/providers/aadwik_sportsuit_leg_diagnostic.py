import bpy, os, json

SOURCE=r"C:\Users\olga_Ashok3\aadwik_character_master_v3.blend"
OUT=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_character_master_v3_sportsuit_diagnostic.blend"
REPORT=r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\reports\aadwik_sportsuit_leg_diagnostic.json"

RIG_NAME="Aadwik_Main_Rig"
CLOTH_NAME="Human.female_sportsuit01"
IK_NAME="foot_ik.L"
POSE_Z=0.09
ZMIN=0.45
ZMAX=0.95

bpy.ops.wm.open_mainfile(filepath=SOURCE)
rig=bpy.data.objects.get(RIG_NAME)
cloth=bpy.data.objects.get(CLOTH_NAME)
if not rig or not cloth:
    raise RuntimeError("Required rig or sportsuit object not found.")

def reset_pose():
    bpy.context.view_layer.objects.active=rig
    if rig.mode!="OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.mode_set(mode="POSE")
    for b in rig.pose.bones:
        b.location=(0,0,0)
        b.rotation_mode="QUATERNION"
        b.rotation_quaternion=(1,0,0,0)
        b.scale=(1,1,1)
    bpy.ops.object.mode_set(mode="OBJECT")

def evaluated_positions(obj):
    dg=bpy.context.evaluated_depsgraph_get()
    ev=obj.evaluated_get(dg)
    mesh=ev.to_mesh()
    try:
        return [v.co.copy() for v in mesh.vertices]
    finally:
        ev.to_mesh_clear()

reset_pose()
neutral=evaluated_positions(cloth)

rig.pose.bones[IK_NAME].location.z=POSE_Z
bpy.context.view_layer.update()
posed=evaluated_positions(cloth)

n=min(len(neutral),len(posed))
rows=[]
for i in range(n):
    if ZMIN <= neutral[i].z <= ZMAX:
        d=posed[i]-neutral[i]
        rows.append((i,d.length,d.x,d.y,d.z,neutral[i].x,neutral[i].y,neutral[i].z))
rows.sort(key=lambda x:x[1],reverse=True)

mods=[]
for m in cloth.modifiers:
    mods.append({
        "name":m.name,
        "type":m.type,
        "show_viewport":m.show_viewport,
        "show_render":m.show_render
    })

def group_stats():
    names=[
        "DEF-thigh.L","DEF-thigh.L.001",
        "DEF-shin.L","DEF-shin.L.001",
        "DEF-knee-helper.L",
        "DEF-pelvis.L","DEF-pelvis-helper.L",
        "DEF-spine","DEF-spine.001"
    ]
    result={}
    groups={g.name:g for g in cloth.vertex_groups}
    for name in names:
        if name not in groups:
            continue
        vg=groups[name]
        vals=[]
        for v in cloth.data.vertices:
            if ZMIN <= v.co.z <= ZMAX:
                try: vals.append(vg.weight(v.index))
                except RuntimeError: pass
        nz=[x for x in vals if x>0.001]
        result[name]={
            "weighted_vertices":len(nz),
            "avg_weight":sum(nz)/len(nz) if nz else 0,
            "max_weight":max(nz) if nz else 0
        }
    return result

avg=sum(r[1] for r in rows)/len(rows) if rows else 0
mx=rows[0][1] if rows else 0

report={
    "source":SOURCE,
    "object":CLOTH_NAME,
    "pose":{"bone":IK_NAME,"z":POSE_Z},
    "region":[ZMIN,ZMAX],
    "neutral_vertices":len(neutral),
    "posed_vertices":len(posed),
    "avg_displacement":avg,
    "max_displacement":mx,
    "top_vertices":[
        {"index":r[0],"displacement":r[1],"dx":r[2],"dy":r[3],"dz":r[4],
         "x":r[5],"y":r[6],"z":r[7]} for r in rows[:30]
    ],
    "modifiers":mods,
    "weight_groups":group_stats(),
    "note":"Read-only sportsuit deformation diagnostic. No weights, rig, modifiers, or clothing geometry were changed."
}

os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,"w",encoding="utf-8") as f:
    json.dump(report,f,indent=2)

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("AADWIK SPORTSUIT DIAGNOSTIC COMPLETE")
print(json.dumps(report,indent=2))
