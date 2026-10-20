import bpy
import sys
from mathutils import Vector

# Aadwik Step 8A — Reusable Stylized Character & Asset Builder
# Blender 5.2.x compatible. Creates reusable named assets for story continuity.

def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=0.65):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.metallic = metallic
    m.roughness = roughness
    return m

SKIN = mat("Tara_Skin", (0.55, 0.28, 0.16))
HAIR = mat("Tara_Hair", (0.035, 0.018, 0.01))
DRESS = mat("Tara_Dress", (0.08, 0.20, 0.55))
WHITE = mat("Eye_White", (0.92, 0.92, 0.92), roughness=0.35)
BLACK = mat("Pupil", (0.01, 0.01, 0.01), roughness=0.25)
CREATURE = mat("Guardian_Body", (0.20, 0.48, 0.62))
SHADOW = mat("Shadow_Creature", (0.025, 0.015, 0.07))
BLUE = mat("Blue_Star", (0.05, 0.35, 1.0), metallic=0.25, roughness=0.2)
GOLD = mat("Star_Glow", (0.9, 0.55, 0.08), metallic=0.1, roughness=0.3)

def uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def cube(name, loc, scale, material, bevel=0.15):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new("Soft_Bevel","BEVEL"); mod.width=bevel; mod.segments=3
    return o

def eye_pair(prefix, y, z, spacing, size):
    for s in (-1,1):
        uv(f"{prefix}_Eye_{'L' if s<0 else 'R'}", (s*spacing, y, z), (size,size,size), WHITE)
        uv(f"{prefix}_Pupil_{'L' if s<0 else 'R'}", (s*spacing, y-size*0.78, z), (size*.42,size*.25,size*.42), BLACK)

def tara():
    root=bpy.data.objects.new("CHAR_TARA_ROOT",None); bpy.context.collection.objects.link(root)
    body=cube("CHAR_TARA_BODY",(0,0,1.45),(.42,.25,.72),DRESS,.12); body.parent=root
    head=uv("CHAR_TARA_HEAD",(0,-.01,2.55),(.48,.42,.52),SKIN); head.parent=root
    # hair cap + side locks
    uv("CHAR_TARA_HAIR",(0,.08,2.82),(.50,.43,.30),HAIR).parent=root
    for x in (-.43,.43):
        uv("CHAR_TARA_HAIR_LOCK",(x,.03,2.55),(.16,.16,.42),HAIR).parent=root
    eye_pair("CHAR_TARA",-0.39,2.61,.18,.075)
    for o in [bpy.context.object]: pass
    # arms / legs
    for x in (-.52,.52):
        cube("CHAR_TARA_ARM",(x,0,1.48),(.11,.13,.48),SKIN,.08).parent=root
    for x in (-.20,.20):
        cube("CHAR_TARA_LEG",(x,0,.48),(.14,.16,.45),SKIN,.07).parent=root
    # small festival sash
    cube("CHAR_TARA_SASH",(0,-.27,1.55),(.43,.035,.10),GOLD,.03).parent=root
    return root

def guardian():
    root=bpy.data.objects.new("CHAR_GUARDIAN_ROOT",None); bpy.context.collection.objects.link(root)
    uv("CHAR_GUARDIAN_BODY",(0,0,1.15),(.62,.48,.70),CREATURE).parent=root
    uv("CHAR_GUARDIAN_HEAD",(0,-.02,2.05),(.48,.40,.46),CREATURE).parent=root
    # ears / horns
    for x in (-.38,.38):
        uv("CHAR_GUARDIAN_EAR",(x,0,2.34),(.16,.12,.32),CREATURE).parent=root
    eye_pair("CHAR_GUARDIAN",-0.36,2.10,.17,.07)
    # injured band
    cube("CHAR_GUARDIAN_BANDAGE",(.48,-.02,1.25),(.06,.35,.18),WHITE,.03).parent=root
    for x in (-.45,.45):
        uv("CHAR_GUARDIAN_FOOT",(x,0,.42),(.20,.28,.16),CREATURE).parent=root
    return root

def shadow():
    root=bpy.data.objects.new("CHAR_SHADOW_ROOT",None); bpy.context.collection.objects.link(root)
    uv("CHAR_SHADOW_BODY",(0,.05,1.45),(.62,.40,1.15),SHADOW)
    for x in (-.48,.48):
        uv("CHAR_SHADOW_ARM",(x,0,1.45),(.18,.18,.72),SHADOW)
    uv("CHAR_SHADOW_HEAD",(0,-.02,2.75),(.52,.38,.52),SHADOW)
    eye_pair("CHAR_SHADOW",-0.36,2.80,.19,.08)
    # silhouette spikes
    for x in (-.35,0,.35):
        uv("CHAR_SHADOW_SPIKE",(x,.03,3.25),(.13,.12,.35),SHADOW)
    return root

def star():
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=.22, location=(0,0,3.2))
    o=bpy.context.object; o.name="PROP_BLUE_STAR"; o.data.materials.append(BLUE)
    bpy.ops.object.shade_smooth()
    return o

clear()
assets=[tara(), guardian(), shadow(), star()]
# Arrange as a clean asset lineup for visual inspection.
assets[0].location=(-2.4,0,0)
assets[1].location=(-.8,0,0)
assets[2].location=(.9,0,0)
assets[3].location=(2.3,0,0)
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath("//aadwik_step8a_assets.blend"))
print("AADWIK_STEP8A_ASSETS_CREATED")
print("TARA=CHAR_TARA_ROOT")
print("GUARDIAN=CHAR_GUARDIAN_ROOT")
print("SHADOW=CHAR_SHADOW_ROOT")
print("STAR=PROP_BLUE_STAR")
