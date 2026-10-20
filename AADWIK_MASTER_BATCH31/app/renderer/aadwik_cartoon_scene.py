# AADWIK BATCH 31 — STORY-AWARE STYLIZED 3D CARTOON RENDERER
# Blender 5.2.x / EEVEE
# CLI: blender -b -P this_file.py -- --frames_dir PATH --width 640 --height 360 --fps 8 --prompt "..."
import bpy, math, os, sys, re, hashlib
from mathutils import Vector

def arg(name, default=None):
    if "--" not in sys.argv:
        return default
    a = sys.argv[sys.argv.index("--")+1:]
    for i,v in enumerate(a):
        if v == name and i+1 < len(a):
            return a[i+1]
    return default

FRAMES_DIR = arg("--frames_dir", os.path.join(os.getcwd(),"frames"))
WIDTH = int(arg("--width","640")); HEIGHT = int(arg("--height","360")); FPS = int(arg("--fps","8"))
PROMPT = arg("--prompt","A curious girl discovers a glowing blue star in a moonlit forest and helps a tiny guardian return home.")
os.makedirs(FRAMES_DIR, exist_ok=True)

SHOTS = 8
SEC_PER_SHOT = 2
FPS = max(4, min(FPS, 12))
FRAMES_PER_SHOT = FPS * SEC_PER_SHOT
TOTAL_FRAMES = SHOTS * FRAMES_PER_SHOT

# ---------- utilities ----------
def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        pass

def mat(name, color, rough=.5, metallic=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color,1)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metallic
        if emission is not None:
            if bsdf.inputs.get("Emission Color"):
                bsdf.inputs["Emission Color"].default_value = (*emission,1)
            elif bsdf.inputs.get("Emission"):
                bsdf.inputs["Emission"].default_value = (*emission,1)
            if bsdf.inputs.get("Emission Strength"):
                bsdf.inputs["Emission Strength"].default_value = strength
    m.diffuse_color=(*color,1)
    return m

def apply_mat(o,m):
    if hasattr(o.data,"materials"): o.data.materials.append(m)
def smooth(o):
    if o.type=="MESH":
        for p in o.data.polygons: p.use_smooth=True
def uv(name, loc, scale, m, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=16, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); apply_mat(o,m); smooth(o)
    return o
def cyl(name, loc, r, depth, m, rot=(0,0,0), seg=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=depth, location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; apply_mat(o,m); smooth(o)
    return o
def cone(name, loc, r1,r2,depth,m,rot=(0,0,0),seg=20):
    bpy.ops.mesh.primitive_cone_add(vertices=seg,radius1=r1,radius2=r2,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; apply_mat(o,m); smooth(o); return o
def torus(name,loc,major,minor,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=28,minor_segments=10,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; apply_mat(o,m); smooth(o); return o
def cube(name,loc,scale,m,bevel=.08):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); apply_mat(o,m)
    if bevel:
        md=o.modifiers.new("Rounded","BEVEL"); md.width=bevel; md.segments=3
    return o
def parent(o,p):
    o.parent=p
def key(o,frame,loc=None,rot=None,scale=None):
    if loc is not None: o.location=loc; o.keyframe_insert("location",frame=frame)
    if rot is not None: o.rotation_euler=rot; o.keyframe_insert("rotation_euler",frame=frame)
    if scale is not None: o.scale=scale; o.keyframe_insert("scale",frame=frame)
def look(o,target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
def camera(name,loc,target,lens=48):
    d=bpy.data.cameras.new(name+"Data"); o=bpy.data.objects.new(name,d); bpy.context.collection.objects.link(o)
    o.location=loc; d.lens=lens; look(o,target); return o
def light(name,loc,energy,color,size=5,target=(0,3,2)):
    d=bpy.data.lights.new(name,"AREA"); d.energy=energy; d.color=color; d.shape="DISK"; d.size=size
    o=bpy.data.objects.new(name,d); bpy.context.collection.objects.link(o); o.location=loc; look(o,target); return o
def point(name,loc,energy,color):
    d=bpy.data.lights.new(name,"POINT"); d.energy=energy; d.color=color; d.shadow_soft_size=1.5
    o=bpy.data.objects.new(name,d); bpy.context.collection.objects.link(o); o.location=loc; return o

# ---------- materials ----------
SKIN=mat("Tara Skin",(0.48,.22,.10),.58)
SKIN_HI=mat("Tara Skin Highlight",(.64,.32,.16),.55)
HAIR=mat("Tara Hair",(.025,.012,.008),.7)
HAIR_HI=mat("Hair Highlight",(.09,.035,.018),.62)
DRESS=mat("Tara Dress",(0.12,.30,.58),.45)
DRESS2=mat("Dress Trim",(.18,.55,.78),.38,metallic=.05)
SHOE=mat("Shoes",(.06,.045,.05),.65)
WHITE=mat("Eye White",(.98,.98,.98),.3)
BLACK=mat("Pupil",(.005,.004,.006),.35)
MOUTH=mat("Mouth",(.20,.012,.025),.5)
GREEN=mat("Forest Green",(.035,.18,.075),.82)
GREEN2=mat("Leaf Green",(.08,.32,.10),.78)
TRUNK=mat("Tree Trunk",(.18,.075,.028),.9)
GROUND=mat("Moss Ground",(.055,.16,.065),.95)
ROCK=mat("Rock",(.12,.13,.16),.95)
MOON=mat("Moon",(.82,.88,.96),.28)
STAR=mat("Magic Blue Star",(.02,.22,.9),.15,emission=(.03,.42,1.0),strength=8)
GUARD=mat("Guardian Body",(.25,.62,.72),.34)
GUARD2=mat("Guardian Belly",(.60,.85,.88),.3)
GOLD=mat("Star Gold",(.95,.55,.06),.25,metallic=.25)
NIGHT=mat("Night Sky",(.006,.012,.045),1)
CLOUD=mat("Cloud",(.18,.22,.30),.95)

# ---------- scene ----------
clear()
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=WIDTH; scene.render.resolution_y=HEIGHT; scene.render.resolution_percentage=100
scene.render.fps=FPS
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
scene.world.color=(.004,.006,.02)
try: scene.view_settings.look="AgX - Medium High Contrast"
except: pass

# world backdrop
cube("SkyBackdrop",(0,12,8),(18,.4,10),NIGHT,0)
# ground
cyl("ForestFloor",(0,4,-.15),10,.3,GROUND,seg=48)
# moon
uv("Moon",(6,8,8.2),(1.25,.25,1.25),MOON)
# stars
seed=int(hashlib.sha256(PROMPT.encode()).hexdigest()[:8],16)
for i in range(34):
    x=((seed+i*37)%240)/10-12
    z=4+((seed+i*71)%100)/10
    y=7.0+(i%5)*.25
    uv("SkyStar%02d"%i,(x,y,z),(.035,.025,.035),WHITE,12)

# ---------- forest ----------
for i in range(18):
    x=-9+(i%9)*2.2 + ((i*13)%7)*.08
    y=3.0+(i//9)*2.0
    z=1.5
    cyl("TreeTrunk%02d"%i,(x,y,z),.28,3.0,TRUNK,seg=12)
    for j in range(3):
        uv("TreeCrown%02d_%d"%(i,j),(x+(j-1)*.55,y,z+2.5+j*.32),(.95,.75,.8),GREEN if j%2==0 else GREEN2,16)
# foreground shrubs
for i in range(20):
    x=-10+(i*1.07)%20; y=-.2+(i%4)*.35
    uv("Bush%02d"%i,(x,y,.45),(.6,.35,.55),GREEN2,16)

# path
cyl("MoonlitPath",(0,2,.03),2.0,.08,mat("Path",(.20,.17,.12),.98),seg=48)

# ---------- Tara character ----------
def make_tara():
    root=bpy.data.objects.new("Tara_Rig",None); bpy.context.collection.objects.link(root)
    parts=[]
    def add(o): parent(o,root); parts.append(o); return o
    add(cyl("TaraLegL",(-.25,0,1.05),.20,1.2,DRESS,rot=(0,0,0)))
    add(cyl("TaraLegR",(.25,0,1.05),.20,1.2,DRESS,rot=(0,0,0)))
    add(uv("TaraShoeL",(-.28,-.08,.45),(.32,.48,.16),SHOE))
    add(uv("TaraShoeR",(.28,-.08,.45),(.32,.48,.16),SHOE))
    add(uv("TaraTorso",(0,0,2.35),(.72,.48,.95),DRESS))
    add(uv("TaraCollar",(0,-.03,2.95),(.42,.38,.20),DRESS2))
    add(cyl("TaraNeck",(0,0,3.15),.18,.3,SKIN,seg=18))
    add(uv("TaraHead",(0,-.03,3.75),(.68,.55,.74),SKIN,28))
    # ears
    add(uv("TaraEarL",(-.62,-.01,3.78),(.12,.12,.18),SKIN))
    add(uv("TaraEarR",(.62,-.01,3.78),(.12,.12,.18),SKIN))
    # hair cap + side locks + bangs
    add(uv("TaraHairCap",(0,.03,4.20),(.73,.58,.45),HAIR,28))
    for i,dx in enumerate([-.55,-.34,-.12,.12,.34,.55]):
        add(uv("TaraBang%d"%i,(dx,-.51,4.08-abs(dx)*.18),(.18,.10,.26),HAIR,16))
    for side in (-1,1):
        add(uv("TaraHairSide%d"%side,(side*.64,.02,3.72),(.20,.22,.48),HAIR,16))
        ex=side*.235
        add(uv("TaraEye%d"%side,(ex,-.545,3.82),(.145,.07,.19),WHITE,20))
        add(uv("TaraPupil%d"%side,(ex,-.607,3.82),(.060,.025,.085),BLACK,16))
    add(uv("TaraNose",(0,-.585,3.62),(.06,.055,.085),SKIN_HI,16))
    add(torus("TaraSmile",(0,-.565,3.46),.105,.022,MOUTH,rot=(math.pi/2,0,0)))
    # arms, hands
    for side in (-1,1):
        add(cyl("TaraArm%d"%side,(side*.78,0,2.42),.17,1.15,SKIN,rot=(0,math.radians(90),0),seg=18))
        add(uv("TaraHand%d"%side,(side*1.36,-.02,2.42),(.19,.19,.19),SKIN_HI,18))
    # backpack
    add(cube("TaraBackpack",(0,.48,2.35),(.40,.18,.58),DRESS2,.10))
    return root

tara=make_tara()
tara.location=(-1.6,1.5,0)

# ---------- tiny guardian ----------
def make_guardian():
    root=bpy.data.objects.new("Guardian_Rig",None); bpy.context.collection.objects.link(root)
    parts=[]
    def add(o): parent(o,root); parts.append(o); return o
    add(uv("GuardianBody",(0,0,1.55),(.62,.48,.55),GUARD,24))
    add(uv("GuardianBelly",(0,-.43,1.52),(.40,.09,.34),GUARD2,20))
    add(uv("GuardianHead",(0,-.02,2.22),(.56,.48,.52),GUARD,24))
    for side in (-1,1):
        add(cone("GuardianEar%d"%side,(side*.45,0,2.55),.25,.02,.62,GUARD2,rot=(0,math.radians(side*18),0),seg=16))
        add(uv("GuardianEye%d"%side,(side*.19,-.47,2.28),(.13,.055,.15),WHITE,20))
        add(uv("GuardianPupil%d"%side,(side*.19,-.52,2.28),(.055,.02,.07),BLACK,16))
    add(torus("GuardianSmile",(0,-.50,2.08),.085,.018,MOUTH,rot=(math.pi/2,0,0)))
    add(uv("GuardianFootL",(-.28,-.05,1.02),(.22,.30,.16),GUARD2,18))
    add(uv("GuardianFootR",(.28,-.05,1.02),(.22,.30,.16),GUARD2,18))
    return root
guardian=make_guardian()
guardian.location=(1.0,4.0,0)

# ---------- magical blue star ----------
star=uv("BlueStar",(0,3.0,2.7),(.32,.12,.32),STAR,24)
for r in (.55,.78):
    torus("StarHalo%02d"%int(r*100),(0,2.86,2.7),r,.018,STAR,rot=(math.pi/2,0,0))

# ---------- animation ----------
# Tara journey, with gentle bob and reactions
tara_keys=[(1,(-1.8,1.7,0)),(16,(-1.55,2.0,0)),(32,(-.7,2.7,0)),(48,(-.35,3.4,0)),
           (64,(-.55,4.1,0)),(80,(-.1,4.9,0)),(96,(.35,5.7,0)),(112,(.7,6.5,0)),(128,(1.0,7.4,0))]
for f,l in tara_keys: key(tara,f,loc=l)
for f in range(1,TOTAL_FRAMES+1,8):
    tara.rotation_euler[2]=math.sin(f*.12)*.025
    tara.keyframe_insert("rotation_euler",frame=f)
# guardian floats toward home
for f,l in [(1,(1.8,4.0,0)),(32,(1.4,4.1,.05)),(48,(.9,4.5,.1)),(64,(.4,5.0,.16)),(80,(0,5.7,.2)),(96,(-.2,6.5,.28)),(112,(-.3,7.3,.35)),(128,(-.2,8.2,.45))]:
    key(guardian,f,loc=l)
for f in range(1,TOTAL_FRAMES+1,8):
    guardian.rotation_euler[2]=math.sin(f*.18)*.08
    guardian.keyframe_insert("rotation_euler",frame=f)
# star pulses and rises
for f,s in [(1,1),(16,1.25),(32,1),(48,1.35),(64,1),(80,1.3),(96,1),(112,1.35),(128,.8)]:
    key(star,f,loc=(0,3.0+(f/128)*3.2,2.7+(f/128)*.8),scale=(s,s,s))
for o in bpy.data.objects:
    if o.name.startswith("StarHalo"):
        for f in (1,32,64,96,128):
            o.rotation_euler[2]=f*.08
            o.keyframe_insert("rotation_euler",frame=f)

# ---------- cameras ----------
cams=[
    camera("Cam01",(10,-12,6.4),(0,3,2.7),44),
    camera("Cam02",(5,-7,4.3),(-.5,2.5,2.8),55),
    camera("Cam03",(-4,-4,4.2),(0,3.8,2.5),58),
    camera("Cam04",(4,-1,3.6),(.2,4.3,2.6),60),
    camera("Cam05",(2,-2,5.0),(.5,5.0,3.0),52),
    camera("Cam06",(-3,-1,3.7),(.3,5.7,2.7),58),
    camera("Cam07",(5,2,4.2),(.5,7.0,2.8),55),
    camera("Cam08",(8,-5,6.2),(.2,6.7,3.0),48),
]
moves=[
 ((10,-12,6.4),(9,-11,6.1)),((5,-7,4.3),(4.5,-6.3,4.1)),
 ((-4,-4,4.2),(-3.5,-3.4,4.0)),((4,-1,3.6),(3.3,-.3,3.4)),
 ((2,-2,5),(1.5,-1.3,4.8)),((-3,-1,3.7),(-2.4,-.3,3.5)),
 ((5,2,4.2),(4.2,2.8,4.0)),((8,-5,6.2),(7,-4.2,6.0))]
for i,c in enumerate(cams):
    s=i*FRAMES_PER_SHOT+1; e=(i+1)*FRAMES_PER_SHOT
    key(c,s,loc=moves[i][0]); key(c,e,loc=moves[i][1])

# ---------- lighting ----------
light("MoonKey",(5,-4,10),1300,(.42,.58,1.0),7,(0,4,2))
light("WarmFill",(-5,-2,5),850,(1.0,.42,.18),5,(0,4,2))
light("Rim",(0,8,7),1000,(.18,.45,1.0),5,(0,6,2))
point("StarGlow",(0,4.5,3.2),900,(.03,.35,1.0))

# ---------- render ----------
print("="*72)
print("AADWIK BATCH 31 — STORY-AWARE STYLIZED 3D CARTOON")
print(f"[AADWIK] Prompt: {PROMPT}")
print(f"[AADWIK] Resolution: {WIDTH}x{HEIGHT} | FPS: {FPS} | Frames: {TOTAL_FRAMES}")
print("[AADWIK] Characters: Tara + Tiny Guardian | World: Moonlit Forest")
print("="*72)

for shot in range(SHOTS):
    start=shot*FRAMES_PER_SHOT+1; end=(shot+1)*FRAMES_PER_SHOT
    scene.frame_start=start; scene.frame_end=end; scene.camera=cams[shot]; scene.frame_set(start)
    scene.render.filepath=os.path.join(FRAMES_DIR,f"shot_{shot+1:02d}_")
    print(f"[AADWIK BLENDER] SHOT {shot+1}/{SHOTS} frames {start}-{end}")
    bpy.ops.render.render(animation=True)

scene.frame_start=1; scene.frame_end=TOTAL_FRAMES; scene.frame_set(1)
count=sum(1 for p in os.scandir(FRAMES_DIR) if p.is_file() and p.name.lower().endswith(".png"))
print(f"[AADWIK BLENDER] CARTOON RENDER COMPLETE | PNG frames: {count}")
