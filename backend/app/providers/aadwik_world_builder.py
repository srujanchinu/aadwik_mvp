import bpy
from mathutils import Vector
from pathlib import Path

WORLD_SPECS={
 "world_village_festival_v1":("Village Festival","village"),
 "world_forest_moonlit_v1":("Moonlit Forest","forest"),
 "world_ancient_tree_v1":("Ancient Tree","ancient_tree"),
 "world_glowing_river_v1":("Glowing River","river"),
 "world_ancient_temple_v1":("Ancient Stone Temple","temple"),
 "world_village_home_v1":("Village Home","home"),
 "world_magical_forest_v1":("Awakened Magical Forest","magical_forest"),
}

def material(name,color,rough=.7):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.roughness=rough
    return m

GROUND=material("WORLD_Ground",(.12,.20,.10))
STONE=material("WORLD_Stone",(.28,.30,.32))
WOOD=material("WORLD_Wood",(.25,.10,.04))
WATER=material("WORLD_GlowingWater",(.03,.25,.55),.25)
LEAF=material("WORLD_Leaf",(.06,.25,.08))
LIGHT=material("WORLD_MagicLight",(.2,.55,1.0),.2)
WARM=material("WORLD_FestivalLight",(1.0,.45,.08),.25)

def cube(name,loc,scale,ma,bevel=.08):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(ma)
    if bevel:
        b=o.modifiers.new("WorldBevel","BEVEL"); b.width=bevel; b.segments=2
    return o

def sphere(name,loc,scale,ma):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(ma); bpy.ops.object.shade_smooth(); return o

def tree(x,y,z=1,magical=False):
    cube("WORLD_Tree_Trunk",(x,y,z),(0.22,.22,1.1),WOOD,.1)
    sphere("WORLD_Tree_Canopy",(x,y,z+1.8),(1.15,1.15,.8),LIGHT if magical else LEAF)

def build_world(world_id):
    if world_id not in WORLD_SPECS: raise ValueError("Unknown world: "+world_id)
    name,kind=WORLD_SPECS[world_id]
    col=bpy.data.collections.new("WORLD_"+world_id)
    bpy.context.scene.collection.children.link(col)
    ground=cube("WORLD_Ground",(0,0,-.15),(6,6,.15),GROUND,.03)
    # move created objects into world collection
    def move(o):
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
    move(ground)

    if kind=="village":
        for x in (-3,3):
            h=cube("WORLD_House",(x,1,1.0),(1.1,.9,1),WOOD,.12); move(h)
            roof=cube("WORLD_Roof",(x,1,2.1),(1.3,1.0,.18),STONE,.06); move(roof)
        for x in (-3,-1,1,3):
            lamp=sphere("WORLD_Festival_Lamp",(x,-1,2.5),(.12,.12,.12),WARM); move(lamp)
    elif kind in ("forest","magical_forest","ancient_tree"):
        for x,y in [(-3,2),(-1,3),(1,2),(3,3),(-3,-2),(3,-2)]:
            tree(x,y,1,kind=="magical_forest")
        if kind=="ancient_tree":
            tree(0,0,1,True)
            for a in range(6):
                import math
                x=math.cos(a*math.pi/3)*1.7; y=math.sin(a*math.pi/3)*1.7
                cube("WORLD_Ancient_Root",(x*.6,y*.6,.15),(0.7,.16,.16),WOOD,.05)
    elif kind=="river":
        water=cube("WORLD_Glowing_River",(0,0,.03),(1.6,6,.04),WATER,.02); move(water)
        for x in (-3,3):
            for y in (-4,-2,0,2,4):
                s=sphere("WORLD_RiverStone",(x,y,.1),(.35,.3,.18),STONE); move(s)
    elif kind=="temple":
        for x in (-3,-1.5,1.5,3):
            p=cube("WORLD_TemplePillar",(x,0,1.5),(.28,.35,1.5),STONE,.08); move(p)
        back=cube("WORLD_TempleWall",(0,2.3,1.5),(3.5,.25,1.5),STONE,.08); move(back)
        for x in (-2,0,2):
            l=sphere("WORLD_TempleLight",(x,1.8,2.5),(.12,.12,.12),LIGHT); move(l)
    elif kind=="home":
        h=cube("WORLD_Home",(0,1,1),(1.8,1.2,1),WOOD,.12); move(h)
        d=cube("WORLD_Door",(0,-.25,.8),(.35,.08,.8),STONE,.04); move(d)

    return col

def clear_worlds():
    for c in list(bpy.data.collections):
        if c.name.startswith("WORLD_world_"):
            bpy.data.collections.remove(c)

def render_preview(world_id,out):
    clear_worlds()
    col=build_world(world_id)
    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE"
    scene.render.resolution_x=320; scene.render.resolution_y=180; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    bpy.ops.object.camera_add(location=(0,-11,4.5))
    cam=bpy.context.object
    cam.rotation_euler=(Vector((0,0,1.2))-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.camera=cam
    scene.render.filepath=str(Path(out).resolve())
    bpy.ops.render.render(write_still=True)
    return col
