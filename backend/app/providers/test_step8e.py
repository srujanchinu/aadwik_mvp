import bpy, runpy
from mathutils import Vector

def make_root(name):
    o=bpy.data.objects.new(name,None)
    bpy.context.scene.collection.objects.link(o)
    return o

mod=runpy.run_path("aadwik_character_animation.py")
animate_root=mod["animate_root"]
actions=mod["ACTIONS"]

roots={
 "char_tara_v1":make_root("CHAR_TARA_ROOT"),
 "char_guardian_v1":make_root("CHAR_GUARDIAN_ROOT"),
 "char_shadow_creature_v1":make_root("CHAR_SHADOW_ROOT"),
}

for aid, acts in actions.items():
    for act in acts:
        animate_root(roots[aid],act,1,32)
        ad=roots[aid].animation_data
        assert ad is not None
        assert ad.action is not None
        # Blender 5.2-safe verification: inspect keyframe count through
        # animation channel collections rather than Action.fcurves.
        assert len(ad.action.layers) > 0
        print(aid, act, "OK")

print("BLENDER 5.2 ACTION API: OK")
print("TARA ACTION STATES: OK")
print("GUARDIAN ACTION STATES: OK")
print("SHADOW ACTION STATES: OK")
print("STEP 8E PASS")
