import bpy
from mathutils import Vector

print("[AADWIK AUTO FIT V1] START")

RIG_NAME = "MAYA_RIGIFY_METARIG_V3"
OUTPUT = r"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_rigify_v3_FITTED.blend"

rig = bpy.data.objects.get(RIG_NAME)
if rig is None:
    raise RuntimeError(f"Armature not found: {RIG_NAME}")
if rig.type != "ARMATURE":
    raise RuntimeError(f"{RIG_NAME} is not an armature")

def bounds(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Missing mesh: {name}")
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))

def center(name):
    a, b = bounds(name)
    return (a + b) * 0.5

def top(name):
    a, b = bounds(name)
    return Vector(((a.x+b.x)*0.5, (a.y+b.y)*0.5, b.z))

pelvis = (center("MAYA_THIGH_L") + center("MAYA_THIGH_R")) * 0.5
chest = center("MAYA_TORSO_MESH")
neck = center("MAYA_NECK")
head = center("MAYA_HEAD")
head_top = top("MAYA_HEAD")

L = {"shoulder":center("MAYA_UPPER_ARM_L"), "elbow":center("MAYA_FOREARM_L"), "hand":center("MAYA_HAND_L"),
     "hip":center("MAYA_THIGH_L"), "knee":center("MAYA_SHIN_L"), "ankle":center("MAYA_ANKLE_L"), "foot":center("MAYA_SHOE_L")}
R = {"shoulder":center("MAYA_UPPER_ARM_R"), "elbow":center("MAYA_FOREARM_R"), "hand":center("MAYA_HAND_R"),
     "hip":center("MAYA_THIGH_R"), "knee":center("MAYA_SHIN_R"), "ankle":center("MAYA_ANKLE_R"), "foot":center("MAYA_SHOE_R")}

inv = rig.matrix_world.inverted()
def local(p): return inv @ p

bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
bones = rig.data.edit_bones

def fit(name, h, t):
    b = bones.get(name)
    if b:
        b.head = local(h)
        b.tail = local(t)
        print("[AADWIK AUTO FIT V1] FIT", name)
    else:
        print("[AADWIK AUTO FIT V1] SKIP", name)

fit("thigh.L", L["hip"], L["knee"])
fit("shin.L", L["knee"], L["ankle"])
fit("foot.L", L["ankle"], L["foot"])
fit("thigh.R", R["hip"], R["knee"])
fit("shin.R", R["knee"], R["ankle"])
fit("foot.R", R["ankle"], R["foot"])

fit("upper_arm.L", L["shoulder"], L["elbow"])
fit("forearm.L", L["elbow"], L["hand"])
fit("hand.L", L["hand"], L["hand"] + Vector((0, -0.10, 0)))
fit("upper_arm.R", R["shoulder"], R["elbow"])
fit("forearm.R", R["elbow"], R["hand"])
fit("hand.R", R["hand"], R["hand"] + Vector((0, -0.10, 0)))

mid = pelvis.lerp(chest, 0.5)
fit("spine", pelvis, mid)
fit("spine.001", mid, chest)
if bones.get("spine.002"): fit("spine.002", chest, neck)
fit("neck", neck, head)
fit("head", head, head_top)

if bones.get("pelvis"):
    tail = pelvis + Vector((0, 0, max(0.08, abs(L["hip"].x-R["hip"].x)*0.15)))
    bones["pelvis"].head = local(pelvis)
    bones["pelvis"].tail = local(tail)

bpy.ops.object.mode_set(mode="OBJECT")
Path = __import__("pathlib").Path
Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
print("[AADWIK AUTO FIT V1] COMPLETE")
print("[AADWIK AUTO FIT V1] OUTPUT:", OUTPUT)
