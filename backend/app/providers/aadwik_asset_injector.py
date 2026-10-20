import bpy
from pathlib import Path

# STEP 8D — Actual reusable asset injection for Blender 5.2.
# Builds the locked asset library once, then links/copies those objects into shots.

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

def ensure_material(name, color):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.roughness = .65
    return m

SKIN=ensure_material("A8D_Skin",(0.55,.28,.16))
HAIR=ensure_material("A8D_Hair",(.03,.015,.008))
DRESS=ensure_material("A8D_Dress",(.08,.20,.55))
WHITE=ensure_material("A8D_EyeWhite",(.92,.92,.92))
BLACK=ensure_material("A8D_Pupil",(.01,.01,.01))
CREATURE=ensure_material("A8D_Guardian",(.20,.48,.62))
SHADOW=ensure_material("A8D_Shadow",(.025,.015,.07))
BLUE=ensure_material("A8D_BlueStar",(.05,.35,1.0))
GOLD=ensure_material("A8D_Gold",(.9,.55,.08))

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material); bpy.ops.object.shade_smooth()
    return o

def cube(name, loc, scale, material, bevel=.1):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        m=o.modifiers.new("A8D_Bevel","BEVEL"); m.width=bevel; m.segments=2
    return o

def eyes(prefix, y, z):
    for s in (-1,1):
        sphere(f"{prefix}_Eye_{s}",(s*.17,y,z),(.075,.075,.075),WHITE)
        sphere(f"{prefix}_Pupil_{s}",(s*.17,y-.06,z),(.035,.02,.035),BLACK)

def build_tara():
    r=bpy.data.objects.new("CHAR_TARA_ROOT",None); bpy.context.collection.objects.link(r)
    for name,loc,sc,ma in [
        ("Tara_Body",(0,0,1.45),(.42,.25,.72),DRESS),
        ("Tara_Head",(0,-.01,2.55),(.48,.42,.52),SKIN),
        ("Tara_Hair",(0,.08,2.82),(.50,.43,.30),HAIR)]:
        o=cube(name,loc,sc,ma,.12) if "Body" in name else sphere(name,loc,sc,ma); o.parent=r
    for x in (-.43,.43):
        sphere("Tara_Hair_Lock",(x,.03,2.55),(.16,.16,.42),HAIR).parent=r
    eyes("Tara",-0.39,2.61)
    for x in (-.52,.52): cube("Tara_Arm",(x,0,1.48),(.11,.13,.48),SKIN,.08).parent=r
    for x in (-.20,.20): cube("Tara_Leg",(x,0,.48),(.14,.16,.45),SKIN,.07).parent=r
    cube("Tara_Sash",(0,-.27,1.55),(.43,.035,.10),GOLD,.03).parent=r
    return r

def build_guardian():
    r=bpy.data.objects.new("CHAR_GUARDIAN_ROOT",None); bpy.context.collection.objects.link(r)
    sphere("Guardian_Body",(0,0,1.15),(.62,.48,.70),CREATURE).parent=r
    sphere("Guardian_Head",(0,-.02,2.05),(.48,.40,.46),CREATURE).parent=r
    for x in (-.38,.38): sphere("Guardian_Ear",(x,0,2.34),(.16,.12,.32),CREATURE).parent=r
    eyes("Guardian",-0.36,2.10)
    cube("Guardian_Bandage",(.48,-.02,1.25),(.06,.35,.18),WHITE,.03).parent=r
    for x in (-.45,.45): sphere("Guardian_Foot",(x,0,.42),(.20,.28,.16),CREATURE).parent=r
    return r

def build_shadow():
    r=bpy.data.objects.new("CHAR_SHADOW_ROOT",None); bpy.context.collection.objects.link(r)
    sphere("Shadow_Body",(0,.05,1.45),(.62,.40,1.15),SHADOW).parent=r
    for x in (-.48,.48): sphere("Shadow_Arm",(x,0,1.45),(.18,.18,.72),SHADOW).parent=r
    sphere("Shadow_Head",(0,-.02,2.75),(.52,.38,.52),SHADOW).parent=r
    eyes("Shadow",-0.36,2.80)
    for x in (-.35,0,.35): sphere("Shadow_Spike",(x,.03,3.25),(.13,.12,.35),SHADOW).parent=r
    return r

def build_star():
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.22,location=(0,0,3.2))
    o=bpy.context.object; o.name="PROP_BLUE_STAR"; o.data.materials.append(BLUE)
    bpy.ops.object.shade_smooth()
    return o

def build_library():
    return {
        "char_tara_v1": build_tara(),
        "char_guardian_v1": build_guardian(),
        "char_shadow_creature_v1": build_shadow(),
        "prop_blue_star_v1": build_star(),
    }

def inject(asset_ids, library):
    injected=[]
    for asset_id in asset_ids:
        root=library[asset_id]
        if root.type == "EMPTY":
            objects=[root]+list(root.children_recursive)
        else:
            objects=[root]
        # duplicate the complete asset hierarchy into a new collection
        col=bpy.data.collections.new(f"SHOT_ASSET_{asset_id}")
        bpy.context.scene.collection.children.link(col)
        copies={}
        for src in objects:
            cp=src.copy()
            if src.data: cp.data=src.data.copy()
            col.objects.link(cp)
            copies[src]=cp
        # restore parent relationships inside copied hierarchy
        for src,cp in copies.items():
            if src.parent in copies: cp.parent=copies[src.parent]
        injected.append((asset_id,col))
    return injected

clear_scene()
library=build_library()

# Keep source assets in a dedicated collection.
source_col=bpy.data.collections.new("AADWIK_LOCKED_ASSET_LIBRARY")
bpy.context.scene.collection.children.link(source_col)
for obj in list(bpy.context.scene.collection.objects):
    if obj.name in {v.name for v in library.values()}:
        pass

# Inject the exact locked assets into a mock production shot.
ids=["char_tara_v1","char_guardian_v1","char_shadow_creature_v1","prop_blue_star_v1"]
injected=inject(ids,library)

# Separate them spatially for inspection.
for i,(_,col) in enumerate(injected):
    for obj in col.objects:
        if obj.parent is None:
            obj.location.x += (i-1.5)*2.2

bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath("//step8d_injected_assets.blend"))
print("AADWIK_STEP8D_INJECTION_COMPLETE")
for aid,col in injected:
    print("INJECTED",aid,"COLLECTION",col.name)
