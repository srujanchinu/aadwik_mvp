# AADWIK BATCH 32 — REAL 3D CARTOON ANIMATION SCENE
# Blender 5.2.x / EEVEE
import bpy, math, os, sys
from mathutils import Vector

def arg(name, default=None):
    a=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    for i,v in enumerate(a):
        if v==name and i+1<len(a): return a[i+1]
    return default

OUT=arg("--frames_dir", os.path.join(os.getcwd(),"frames"))
W=int(arg("--width","640")); H=int(arg("--height","360")); FPS=int(arg("--fps","8"))
PROMPT=arg("--prompt","A curious girl discovers a glowing blue star in a moonlit forest and helps a tiny guardian return home.")
os.makedirs(OUT,exist_ok=True)

def clear():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)

def material(name,c,rough=.55,emit=None,strength=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value=(*c,1); b.inputs["Roughness"].default_value=rough
        if emit is not None:
            if b.inputs.get("Emission Color"): b.inputs["Emission Color"].default_value=(*emit,1)
            if b.inputs.get("Emission Strength"): b.inputs["Emission Strength"].default_value=strength
    return m
def apply(o,m):
    if hasattr(o.data,"materials"): o.data.materials.append(m)
def sphere(n,l,s,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=l)
    o=bpy.context.object;o.name=n;o.scale=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);apply(o,m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def cyl(n,l,r,d,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=d,location=l,rotation=rot)
    o=bpy.context.object;o.name=n;apply(o,m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def cube(n,l,s,m,b=.08):
    bpy.ops.mesh.primitive_cube_add(location=l);o=bpy.context.object;o.name=n;o.scale=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);apply(o,m)
    if b:
        mod=o.modifiers.new("SoftEdges","BEVEL");mod.width=b;mod.segments=3
    return o
def parent(o,p): o.parent=p
def key(o,f,loc=None,rot=None,scale=None):
    if loc is not None:o.location=loc;o.keyframe_insert("location",frame=f)
    if rot is not None:o.rotation_euler=rot;o.keyframe_insert("rotation_euler",frame=f)
    if scale is not None:o.scale=scale;o.keyframe_insert("scale",frame=f)
def look(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat("-Z","Y").to_euler()
def cam(n,l,t,lens=52):
    d=bpy.data.cameras.new(n+"Data");o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=l;d.lens=lens;look(o,t);return o
def area(n,l,e,c,size,t):
    d=bpy.data.lights.new(n,"AREA");d.energy=e;d.color=c;d.shape="DISK";d.size=size
    o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=l;look(o,t);return o
def point(n,l,e,c):
    d=bpy.data.lights.new(n,"POINT");d.energy=e;d.color=c;d.shadow_soft_size=1.2
    o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=l;return o

clear()
scene=bpy.context.scene;scene.render.engine="BLENDER_EEVEE";scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=100
scene.render.fps=FPS;scene.render.image_settings.file_format="PNG";scene.world.color=(.004,.007,.025)
try: scene.view_settings.look="AgX - Medium High Contrast"
except: pass

SKIN=material("Skin",(.52,.25,.12),.55); HAIR=material("Hair",(.018,.008,.004),.7)
DRESS=material("Dress",(.10,.28,.62),.45); TRIM=material("Trim",(.20,.58,.82),.35)
SHOE=material("Shoes",(.035,.025,.03),.7); WHITE=material("Eyes",(.98,.98,.98),.25); BLACK=material("Pupils",(.003,.003,.005),.25)
MOUTH=material("Mouth",(.18,.008,.015),.4); GREEN=material("Tree",(.025,.15,.055),.9); LEAF=material("Leaves",(.06,.29,.08),.85)
TRUNK=material("Trunk",(.16,.065,.025),.95); GROUND=material("Ground",(.045,.14,.055),1); PATH=material("Path",(.19,.15,.10),1)
NIGHT=material("Sky",(.005,.009,.035),1); MOON=material("Moon",(.8,.88,.98),.3); ROCK=material("Rock",(.11,.12,.15),1)
GUARD=material("Guardian",(.22,.58,.7),.38); BELLY=material("GuardianBelly",(.58,.84,.86),.3)
STAR=material("MagicStar",(.02,.20,.9),.18,emit=(.02,.4,1),strength=10)

# World
cube("Sky",(0,8,7),(18,.4,10),NIGHT,0); cyl("Ground",(0,4,-.2),11,.35,GROUND)
sphere("Moon",(6,7.8,8),(1.25,.22,1.25),MOON)
for i in range(25):
    x=-10+(i*1.73)%20; z=5+(i%7)*.48
    sphere("StarSky%02d"%i,(x,7,z),(.035,.02,.035),WHITE)

# forest depth layers
for i in range(22):
    x=-10+(i%11)*2; y=2.2+(i//11)*2.5
    cyl("Trunk%02d"%i,(x,y,1.6),.28,3.2,TRUNK)
    sphere("CrownA%02d"%i,(x,y,3.35),(.95,.72,.8),GREEN)
    sphere("CrownB%02d"%i,(x+.45,y,3.75),(.72,.55,.65),LEAF)
# path
cyl("Path",(0,2,.03),2.1,.08,PATH)

# ---------- articulated Tara ----------
def tara():
    rig=bpy.data.objects.new("Tara_Rig",None);bpy.context.collection.objects.link(rig)
    # torso root at world-relative origin
    body=sphere("TaraTorso",(0,0,2.3),(.65,.45,.9),DRESS);parent(body,rig)
    neck=cyl("TaraNeck",(0,0,3.15),.17,.3,SKIN);parent(neck,rig)
    head=sphere("TaraHead",(0,0,3.72),(.67,.54,.72),SKIN);parent(head,rig)
    hair=sphere("TaraHair",(0,.02,4.18),(.72,.57,.43),HAIR);parent(hair,rig)
    for i,x in enumerate([-.5,-.28,0,.28,.5]):
        b=sphere("Bang%d"%i,(x,-.5,4.05-abs(x)*.18),(.16,.08,.25),HAIR);parent(b,rig)
    for side in (-1,1):
        eye=sphere("Eye%d"%side,(side*.23,-.52,3.82),(.145,.055,.18),WHITE);parent(eye,rig)
        pup=sphere("Pupil%d"%side,(side*.23,-.57,3.82),(.06,.022,.08),BLACK);parent(pup,rig)
        ear=sphere("Ear%d"%side,(side*.62,0,3.78),(.12,.12,.18),SKIN);parent(ear,rig)
    mouth=cube("Mouth",(0,-.54,3.48),(.09,.025,.025),MOUTH,.02);parent(mouth,rig)
    # articulated limbs are separate objects parented to torso root; rotations create visible motion
    arms=[]; legs=[]
    for side in (-1,1):
        arm=cyl("Arm%d"%side,(side*.72,0,2.45),.16,1.15,SKIN,rot=(0,math.radians(90),0));parent(arm,rig);arms.append(arm)
        hand=sphere("Hand%d"%side,(side*1.28,-.01,2.45),(.18,.18,.18),SKIN);parent(hand,rig)
        leg=cyl("Leg%d"%side,(side*.24,0,1.15),.19,1.15,DRESS);parent(leg,rig);legs.append(leg)
        shoe=sphere("Shoe%d"%side,(side*.24,-.10,.5),(.28,.42,.15),SHOE);parent(shoe,rig)
    backpack=cube("Backpack",(0,.43,2.35),(.38,.18,.55),TRIM,.12);parent(backpack,rig)
    return rig,arms,legs,mouth

TARA, TARA_ARMS, TARA_LEGS, TARA_MOUTH=tara()
TARA.location=(-2,1.5,0)

# Guardian with bobbing articulated feel
def guardian():
    r=bpy.data.objects.new("Guardian_Rig",None);bpy.context.collection.objects.link(r)
    body=sphere("GuardianBody",(0,0,1.55),(.58,.45,.5),GUARD);parent(body,r)
    belly=sphere("GuardianBelly",(0,-.42,1.52),(.38,.08,.30),BELLY);parent(belly,r)
    head=sphere("GuardianHead",(0,-.02,2.15),(.54,.46,.5),GUARD);parent(head,r)
    for side in (-1,1):
        ear=cyl("GuardianEar%d"%side,(side*.42,0,2.52),.19,.48,BELLY,rot=(0,math.radians(side*22),0));parent(ear,r)
        eye=sphere("GuardianEye%d"%side,(side*.19,-.46,2.22),(.12,.05,.14),WHITE);parent(eye,r)
        pup=sphere("GuardianPupil%d"%side,(side*.19,-.51,2.22),(.05,.02,.07),BLACK);parent(pup,r)
    mouth=cube("GuardianMouth",(0,-.48,2.04),(.07,.02,.025),MOUTH,.01);parent(mouth,r)
    for side in (-1,1):
        foot=sphere("Foot%d"%side,(side*.25,-.04,1.05),(.21,.28,.14),BELLY);parent(foot,r)
    return r
GUARDIAN=guardian();GUARDIAN.location=(1.5,4.0,0)

# Star
STAROBJ=sphere("BlueStar",(0,3,2.65),(.34,.12,.34),STAR)
for f in range(1,129,8):
    s=1+0.18*math.sin(f*.22); key(STAROBJ,f,scale=(s,s,s))

# animation: walking cycle and expressive gestures
FPS=max(4,min(FPS,12)); SHOTS=8; SPF=2*FPS; TOTAL=SHOTS*SPF
# journey
positions=[(-2,1.4,0),(-1.4,2.0,0),(-.8,2.8,0),(-.35,3.6,0),(.0,4.4,0),(.45,5.2,0),(.8,6.0,0),(1.0,6.8,0)]
for shot,pos in enumerate(positions):
    s=shot*SPF+1;e=(shot+1)*SPF
    key(TARA,s,loc=pos); key(TARA,e,loc=(pos[0]+.18,pos[1]+.25,pos[2]))
    # walk bounce
    for f in range(s,e+1,2):
        phase=(f-s)/(e-s)*math.pi*2
        TARA.location.z=0.06*max(0,math.sin(phase*2))
        TARA.keyframe_insert("location",frame=f)
        swing=.42*math.sin(phase)
        TARA_ARMS[0].rotation_euler[1]=swing; TARA_ARMS[0].keyframe_insert("rotation_euler",frame=f)
        TARA_ARMS[1].rotation_euler[1]=-swing; TARA_ARMS[1].keyframe_insert("rotation_euler",frame=f)
        TARA_LEGS[0].rotation_euler[1]=-swing*.7; TARA_LEGS[0].keyframe_insert("rotation_euler",frame=f)
        TARA_LEGS[1].rotation_euler[1]=swing*.7; TARA_LEGS[1].keyframe_insert("rotation_euler",frame=f)
# gesture/reaction beats
for f,rot in [(SPF*3+1,-.55),(SPF*4+1,.6),(SPF*5+1,-.25),(SPF*6+1,.25)]:
    TARA_ARMS[1].rotation_euler[1]=rot;TARA_ARMS[1].keyframe_insert("rotation_euler",frame=f)
# guardian homeward flight
for f,loc in [(1,(1.6,4,0)),(SPF*2,(1.1,4.5,.2)),(SPF*4,(.5,5.3,.4)),(SPF*6,(0,6.3,.6)),(SPF*8,(-.3,7.4,.9))]:
    key(GUARDIAN,f,loc=loc)
for f in range(1,TOTAL+1,2):
    GUARDIAN.rotation_euler[2]=.12*math.sin(f*.18);GUARDIAN.rotation_euler[2] = GUARDIAN.rotation_euler[2]
    GUARDIAN.keyframe_insert("rotation_euler",frame=f)

# cameras, each shot has a small push/pan instead of a static camera
cams=[
cam("Shot01",(9,-11,6.2),(0,3,2.5),45),
cam("Shot02",(4,-7,4.4),(-.8,2.7,2.9),58),
cam("Shot03",(-3,-4,3.9),(-.4,3.6,2.8),62),
cam("Shot04",(3,-2,3.6),(-.1,4.2,2.8),62),
cam("Shot05",(1,-2.2,4.4),(.1,4.8,3.0),60),
cam("Shot06",(-2,-1.5,4.0),(.5,5.6,2.9),62),
cam("Shot07",(4,1,4.5),(.6,6.5,3.1),56),
cam("Shot08",(7,-5,5.8),(.2,6.7,3.0),48)]
for i,c in enumerate(cams):
    s=i*SPF+1;e=(i+1)*SPF
    loc=c.location.copy(); key(c,s,loc=loc); key(c,e,loc=(loc.x*.94,loc.y+.7,loc.z+.12))

area("MoonLight",(5,-3,10),1250,(.38,.55,1),7,(0,4,2))
area("WarmFill",(-5,-2,5),700,(1,.38,.16),5,(0,4,2))
area("Rim",(0,7,8),900,(.18,.42,1),5,(0,6,2))
point("StarLight",(0,4.5,3.2),1100,(.03,.35,1))

print("="*70);print("AADWIK BATCH 32 — REAL 3D CARTOON ANIMATION");print(f"PROMPT: {PROMPT}");print(f"FPS={FPS} TOTAL_FRAMES={TOTAL}");print("="*70)
for i,c in enumerate(cams):
    s=i*SPF+1;e=(i+1)*SPF;scene.camera=c;scene.frame_start=s;scene.frame_end=e;scene.frame_set(s)
    scene.render.filepath=os.path.join(OUT,f"shot_{i+1:02d}_")
    print(f"[AADWIK ANIMATION] SHOT {i+1}/8")
    bpy.ops.render.render(animation=True)
count=len(list(__import__("pathlib").Path(OUT).rglob("*.png")))
print(f"[AADWIK ANIMATION] COMPLETE — PNG frames: {count}")
