import bpy
from mathutils import Vector

# STEP 8E FIX — Blender 5.2-safe animation authoring.
# Do not access Action.fcurves; Blender 5.2 changed the Action API.
# keyframe_insert() is sufficient for this lightweight animation layer.

def key(obj, frame, loc=None, rot=None):
    if loc is not None:
        obj.location=loc
        obj.keyframe_insert(data_path="location", frame=frame)
    if rot is not None:
        obj.rotation_euler=rot
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)

def animate_root(root, action, start=1, end=32):
    root.animation_data_clear()
    base=root.location.copy()
    if action=="idle":
        key(root,start,base)
        key(root,end,base+Vector((0,0,.03)))
    elif action=="look":
        key(root,start,base,(0,0,0))
        key(root,start+8,base+Vector((0,0,.03)),(0,.12,0))
        key(root,end,base,(0,0,0))
    elif action=="walk":
        key(root,start,base,(0,0,0))
        key(root,start+12,base+Vector((.45,0,0)))
        key(root,start+24,base+Vector((.9,0,0)))
        key(root,end,base+Vector((1.15,0,0)))
    elif action=="reach":
        key(root,start,base,(0,0,0))
        key(root,start+10,base+Vector((0,-.05,.04)),(0,-.12,0))
        key(root,end,base,(0,0,0))
    elif action=="threaten":
        key(root,start,base,(0,0,0))
        key(root,start+8,base+Vector((0,.03,.08)),(0,.10,0))
        key(root,start+16,base+Vector((0,-.03,0)),(0,-.12,0))
        key(root,end,base,(0,0,0))
    elif action=="injured":
        key(root,start,base,(0,0,.04))
        key(root,start+12,base+Vector((-.05,0,0)),(0,0,-.08))
        key(root,end,base,(0,0,.04))
    else:
        raise ValueError("Unknown action: "+action)

ACTIONS={
 "char_tara_v1":["idle","look","walk","reach"],
 "char_guardian_v1":["idle","injured","look"],
 "char_shadow_creature_v1":["idle","threaten","look"],
}
print("AADWIK_STEP8E_ANIMATION_MODULE_READY")
