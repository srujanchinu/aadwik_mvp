
import bpy, sys, json, math
from pathlib import Path
from mathutils import Vector

def args():
    a=sys.argv
    return a[a.index("--")+1:]

def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        pass

def mat(name, color, metallic=0.0, rough=0.6, emission=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value=(*color,1)
        bs.inputs["Roughness"].default_value=rough
        bs.inputs["Metallic"].default_value=metallic
        if emission:
            bs.inputs["Emission Color"].default_value=(*color,1)
            bs.inputs["Emission Strength"].default_value=emission
    return m

def cube(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material); return o

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material); return o

def cylinder(name, loc, radius, depth, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material); return o

def tree(x,y,z,green,bark):
    cylinder("TreeTrunk",(x,y,z+1.5),.25,3,bark)
    sphere("TreeCanopy",(x,y,z+3.3),(1.3,1.3,1.2),green)

def character(name, x,y,z, body, skin, scale=1.0):
    cube(name+"_Body",(x,y,z+1.05),(.38*scale,.28*scale,.7*scale),body)
    sphere(name+"_Head",(x,y,z+2.0),(.36*scale,.32*scale,.36*scale),skin)
    cylinder(name+"_LegL",(x-.16*scale,y,z+.3),.10*scale,.6*scale,body)
    cylinder(name+"_LegR",(x+.16*scale,y,z+.3),.10*scale,.6*scale,body)

def environment(location):
    ground=mat("Ground",(0.08,0.11,0.09),rough=.9)
    wood=mat("Wood",(0.20,0.12,0.07),rough=.85)
    green=mat("Leaves",(0.08,0.25,0.10),rough=.8)
    stone=mat("Stone",(0.25,0.27,0.30),rough=.9)
    water=mat("GlowWater",(0.04,0.25,0.35),rough=.25,emission=.25)
    gold=mat("FestivalGold",(0.8,0.45,0.08),metallic=.2)
    cube("Ground",(0,0,-.15),(12,12,.15),ground)
    loc=location.lower()
    if "village" in loc:
        for x in (-6,-3,3,6): cube("House",(x,3,1.5),(1.4,1.2,1.5),wood)
        for x in range(-5,7,2): sphere("Lantern",(x,-1.5,3),(0.15,.15,.25),gold)
    elif "forest" in loc or "tree" in loc:
        for x,y in [(-6,2),(-3,4),(3,4),(6,2),(-5,-3),(5,-3)]:
            tree(x,y,0,green,wood)
    elif "river" in loc:
        cube("River",(0,0,.02),(8,1.8,.05),water)
        for x in (-5,-2,2,5): cube("Bank",(x,2,.1),(1.2,1,.15),ground)
    elif "temple" in loc:
        for x in (-4,-2,0,2,4): cylinder("TempleColumn",(x,2,2),.45,4,stone)
        cube("TempleBack",(0,4,3),(5,.4,3),stone)
        cube("TempleFloor",(0,0,.05),(6,5,.08),stone)
    elif "sky" in loc:
        sphere("Moon",(4,5,8),(1.5,1.5,1.5),gold)
    else:
        cube("Home",(0,4,1.5),(2,1.5,1.5),wood)
    return locals()

def make_camera(shot, index):
    framing=shot.get("framing","medium")
    distance={"wide":12,"medium":7,"close_up":4,"close":4}.get(framing,7)
    bpy.ops.object.camera_add(location=(0,-distance,5))
    cam=bpy.context.object
    cam.name=shot["shot_id"]+"_Camera"
    lens=int(str(shot.get("lens","50mm")).replace("mm",""))
    cam.data.lens=lens
    target=Vector((0,0,1.6))
    direction=target-cam.location
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    bpy.context.scene.camera=cam
    return cam

def make_lighting(shot):
    bpy.ops.object.light_add(type="AREA",location=(0,-4,8))
    key=bpy.context.object; key.data.energy=1100; key.data.shape="DISK"; key.data.size=6
    bpy.ops.object.light_add(type="POINT",location=(2,0,4))
    fill=bpy.context.object; fill.data.energy=250

def render_shot(shot, outdir, index):
    clear()
    environment(shot["location"])
    human=mat("TaraClothes",(0.25,0.18,0.45))
    skin=mat("Skin",(0.55,0.30,0.20))
    guardian_mat=mat("Guardian",(0.15,0.45,0.35),emission=.1)
    shadow_mat=mat("Shadow",(0.015,0.015,0.02),rough=.95)
    names=shot.get("characters",[])
    positions=[(-1.4,0,0),(0,0,0),(1.5,0,0)]
    for i,n in enumerate(names[:3]):
        if n=="tara": character("Tara",*positions[i],human,skin)
        elif n=="guardian": sphere("Guardian",positions[i],(.55,.45,.45),guardian_mat)
        elif n=="shadow_creature":
            sphere("ShadowCreature",positions[i],(.8,.5,1.2),shadow_mat)
    if "blue_star" in shot.get("props",[]) or "star" in shot.get("story_context","").lower():
        star=mat("BlueStar",(0.03,0.35,1.0),emission=4)
        sphere("BlueStar",(0,0,3),(.28,.28,.28),star)
    make_camera(shot,index); make_lighting(shot)
    sc=bpy.context.scene
    sc.render.engine="BLENDER_EEVEE"
    sc.render.resolution_x=640; sc.render.resolution_y=360; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG"
    sc.render.filepath=str(Path(outdir)/(shot["shot_id"]+".png"))
    sc.render.film_transparent=False
    sc.render.resolution_percentage=100
    bpy.ops.render.render(write_still=True)

def main():
    a=args()
    if len(a)<2: raise SystemExit("Usage: blender ... -- job.json output_dir [shot_limit]")
    job=json.loads(Path(a[0]).read_text(encoding="utf-8"))
    out=Path(a[1]); limit=int(a[2]) if len(a)>2 else 2
    for i,shot in enumerate(job["shots"][:limit]):
        print("AADWIK_RENDER_SHOT",shot["shot_id"],shot["location"],shot["story_context"])
        render_shot(shot,out,i)
    print("AADWIK_BLENDER_JOB_COMPLETE",min(limit,len(job["shots"])))

main()
