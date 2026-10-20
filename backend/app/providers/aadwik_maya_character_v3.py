
import bpy, sys, math, argparse
from mathutils import Vector

print("[AADWIK MAYA V3] MASTER CHARACTER ASSET - SINGLE FRAME")

# ---------- materials ----------
def make_mat(name, color, rough=.4, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value = (*color, 1)
        bs.inputs["Roughness"].default_value = rough
        bs.inputs["Metallic"].default_value = metallic
    return m

# ---------- geometry ----------
def smooth(obj):
    if hasattr(obj.data, "polygons"):
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj

def uv(name, loc, scale, material, seg=64, rings=40):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=seg, ring_count=rings, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return smooth(o)

def capsule(name, a, b, radius, material):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=radius, depth=d.length, location=(a+b)/2
    )
    o = bpy.context.object
    o.name = name
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    o.data.materials.append(material)
    bevel = o.modifiers.new("Rounded edges", "BEVEL")
    bevel.width = radius * .55
    bevel.segments = 5
    return smooth(o)

def lathe(name, profile, material, segments=64):
    # profile: [(radius,z), ...]
    verts=[]
    faces=[]
    for r,z in profile:
        for i in range(segments):
            a=2*math.pi*i/segments
            verts.append((r*math.cos(a), r*math.sin(a), z))
    rows=len(profile)
    for j in range(rows-1):
        for i in range(segments):
            a=j*segments+i
            b=j*segments+(i+1)%segments
            c=(j+1)*segments+(i+1)%segments
            d=(j+1)*segments+i
            faces.append((a,b,c,d))
    # caps
    verts.append((0,0,profile[0][1])); bot=len(verts)-1
    verts.append((0,0,profile[-1][1])); top=len(verts)-1
    for i in range(segments):
        ni=(i+1)%segments
        faces.append((bot,ni,i))
        a=(rows-1)*segments+i
        b=(rows-1)*segments+ni
        faces.append((top,a,b))
    mesh=bpy.data.meshes.new(name+"_MESH")
    mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return smooth(o)

def curve_tube(name, points, bevel, material):
    cu=bpy.data.curves.new(name+"_CURVE","CURVE")
    cu.dimensions="3D"; cu.resolution_u=4
    cu.bevel_depth=bevel; cu.bevel_resolution=5
    sp=cu.splines.new("BEZIER"); sp.bezier_points.add(len(points)-1)
    for bp,p in zip(sp.bezier_points,points):
        bp.co=Vector(p); bp.handle_left_type="AUTO"; bp.handle_right_type="AUTO"
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    return ob

# ---------- character ----------
def build_maya():
    skin = make_mat("Maya Skin",(0.72,0.36,0.20),.5)
    hair = make_mat("Maya Hair",(0.018,0.008,0.004),.3)
    dress = make_mat("Maya Dress",(0.07,0.25,0.70),.36)
    dress2 = make_mat("Maya Dress Trim",(0.10,0.48,0.88),.34)
    scarf = make_mat("Maya Scarf",(0.03,0.70,0.86),.3)
    white = make_mat("Eye White",(0.98,0.98,0.95),.18)
    iris = make_mat("Iris",(0.035,0.24,0.55),.2)
    black = make_mat("Dark",(0.004,0.003,0.003),.24)
    shoe = make_mat("Shoes",(0.025,0.04,0.09),.3)
    sole = make_mat("Sole",(0.012,0.015,0.025),.4)

    # Custom lathed torso gives a continuous, designed silhouette rather than a blob.
    torso_profile=[
        (.28,1.75),(.40,1.85),(.55,2.05),(.62,2.35),
        (.64,2.70),(.60,3.00),(.50,3.30),(.38,3.48),(.25,3.55)
    ]
    torso=lathe("MAYA_TORSO_MESH",torso_profile,skin)
    # Dress fitted over torso, with waist and hem shaping.
    dress_profile=[
        (.30,1.86),(.43,1.92),(.56,2.10),(.66,2.38),
        (.68,2.70),(.64,2.98),(.54,3.20),(.39,3.37),(.25,3.40)
    ]
    lathe("MAYA_DRESS_MESH",dress_profile,dress)

    # Neck + head
    capsule("MAYA_NECK",(0,0,3.35),(0,0,3.68),.20,skin)
    uv("MAYA_HEAD",(0,0,4.18),(.57,.49,.64),skin)

    # ears
    uv("MAYA_EAR_L",(-.53,0,4.18),(.11,.07,.17),skin)
    uv("MAYA_EAR_R",(.53,0,4.18),(.11,.07,.17),skin)

    # Arms with intentional elbow and wrist joints, hands + five small fingers.
    for side,x in (("L",-1),("R",1)):
        sh=(.57*x,-.005,3.00); el=(.78*x,-.025,2.42); wr=(.80*x,-.06,1.98)
        capsule("MAYA_UPPER_ARM_"+side,sh,el,.17,skin)
        capsule("MAYA_FOREARM_"+side,el,wr,.145,skin)
        uv("MAYA_HAND_"+side,(.80*x,-.07,1.83),(.19,.15,.23),skin)
        for fi in range(5):
            # fan of fingers in x/z plane
            fx=.80*x + x*(fi-2)*.045
            fz=1.72 + (0.035 if fi in (1,2,3) else 0)
            capsule("MAYA_FINGER_%s_%d"%(side,fi),(fx,-.12,fz),(fx+x*.025,-.15,fz-.11),.035,skin)

    # Legs: thigh, shin, small ankle and designed shoes.
    for side,x in (("L",-1),("R",1)):
        hip=(.28*x,0,1.78); knee=(.30*x,-.005,.95); ankle=(.30*x,-.015,.30)
        capsule("MAYA_THIGH_"+side,hip,knee,.22,skin)
        capsule("MAYA_SHIN_"+side,knee,ankle,.17,skin)
        uv("MAYA_ANKLE_"+side,(.30*x,-.02,.23),(.15,.14,.16),skin)
        uv("MAYA_SHOE_"+side,(.30*x,-.14,.13),(.30,.48,.15),shoe)
        uv("MAYA_SOLE_"+side,(.30*x,-.15,.055),(.32,.50,.065),sole)

    # Hair cap and designed locks/fringe. Curves create controlled strands/silhouette.
    uv("MAYA_HAIR_CAP",(0,.015,4.58),(.59,.51,.39),hair)
    curve_tube("MAYA_HAIR_FRINGE",
        [(-.45,-.40,4.55),(-.22,-.52,4.66),(0,-.54,4.58),(.23,-.52,4.66),(.45,-.40,4.55)],
        .10,hair)
    curve_tube("MAYA_HAIR_LEFT",
        [(-.51,.00,4.48),(-.58,-.01,4.08),(-.50,-.01,3.72),(-.37,-.01,3.55)],
        .105,hair)
    curve_tube("MAYA_HAIR_RIGHT",
        [(.51,.00,4.48),(.58,-.01,4.08),(.50,-.01,3.72),(.37,-.01,3.55)],
        .105,hair)

    # Expressive face, positioned toward camera (-Y).
    for x in (-.205,.205):
        uv("MAYA_EYE_"+str(x),(x,-.468,4.30),(.135,.055,.155),white,48,32)
        uv("MAYA_IRIS_"+str(x),(x,-.522,4.30),(.060,.018,.073),iris,40,24)
        uv("MAYA_PUPIL_"+str(x),(x,-.542,4.30),(.027,.010,.038),black,32,20)
        brow=curve_tube("MAYA_BROW_"+str(x),
            [(x-.11,-.48,4.49),(x,-.505,4.52),(x+.11,-.48,4.49)],.025,black)
    uv("MAYA_NOSE",(0,-.505,4.08),(.055,.065,.085),skin,40,24)
    # small smile curve
    curve_tube("MAYA_SMILE",
        [(-.105,-.515,3.94),(-.05,-.535,3.91),(0,-.54,3.90),
         (.05,-.535,3.91),(.105,-.515,3.94)],.025,black)

    # Scarf collar with a small trailing end.
    uv("MAYA_SCARF_COLLAR",(0,-.46,3.62),(.37,.07,.095),scarf,48,24)
    curve_tube("MAYA_SCARF_TAIL",
        [(.24,-.43,3.60),(.40,-.38,3.34),(.34,-.32,3.08)],.075,scarf)

    # identity + asset metadata
    bpy.ops.object.armature_add(location=(0,0,.10))
    rig=bpy.context.object; rig.name="MAYA_MASTER_RIG_V3"
    bpy.ops.object.mode_set(mode="EDIT")
    root=rig.data.edit_bones[0]; root.name="root"; root.head=(0,0,.1); root.tail=(0,0,1)
    spine=rig.data.edit_bones.new("spine"); spine.head=(0,0,1); spine.tail=(0,0,3.35); spine.parent=root
    neck=rig.data.edit_bones.new("neck"); neck.head=(0,0,3.35); neck.tail=(0,0,3.75); neck.parent=spine
    head=rig.data.edit_bones.new("head"); head.head=(0,0,3.75); head.tail=(0,0,4.75); head.parent=neck
    for side,x in (("L",-1),("R",1)):
        u=rig.data.edit_bones.new("upper_arm_"+side); u.head=(.57*x,0,3); u.tail=(.78*x,0,2.42); u.parent=spine
        f=rig.data.edit_bones.new("forearm_"+side); f.head=(.78*x,0,2.42); f.tail=(.80*x,0,1.98); f.parent=u
        h=rig.data.edit_bones.new("hand_"+side); h.head=(.80*x,0,1.98); h.tail=(.80*x,0,1.7); h.parent=f
        t=rig.data.edit_bones.new("thigh_"+side); t.head=(.28*x,0,1.78); t.tail=(.30*x,0,.95); t.parent=spine
        s=rig.data.edit_bones.new("shin_"+side); s.head=(.30*x,0,.95); s.tail=(.30*x,0,.30); s.parent=t
        ft=rig.data.edit_bones.new("foot_"+side); ft.head=(.30*x,0,.30); ft.tail=(.30*x,-.30,.10); ft.parent=s
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.hide_viewport=True; rig.hide_render=True
    rig["character_id"]="char_maya_v3"
    rig["identity_locked"]=True
    rig["asset_type"]="master_stylized_3d_character"
    rig["single_frame_gate"]=True
    return rig

def main():
    argv=sys.argv
    if "--" in argv: argv=argv[argv.index("--")+1:]
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--width",type=int,default=640)
    ap.add_argument("--height",type=int,default=640)
    args=ap.parse_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    build_maya()

    floor=make_mat("Studio Floor",(.025,.032,.05),.7)
    bpy.ops.mesh.primitive_plane_add(size=25,location=(0,0,0))
    bpy.context.object.data.materials.append(floor)

    world=bpy.data.worlds.new("AADWIK_WORLD_V3")
    bpy.context.scene.world=world
    world.color=(.005,.008,.018)

    # Key/fill/rim
    for name,loc,energy,size in [
        ("Key",(-4,-6,7),1200,4.5),
        ("Fill",(4,-5,5),650,3.5),
        ("Rim",(0,3,7),1400,3.0),
    ]:
        bpy.ops.object.light_add(type="AREA",location=loc)
        l=bpy.context.object; l.name=name
        l.data.energy=energy; l.data.shape="DISK"; l.data.size=size
        l.rotation_euler=(Vector((0,0,2.7))-l.location).to_track_quat("-Z","Y").to_euler()

    bpy.ops.object.camera_add(location=(0,-11.5,3.0))
    cam=bpy.context.object; cam.data.lens=60
    cam.rotation_euler=(Vector((0,0,2.65))-cam.location).to_track_quat("-Z","Y").to_euler()
    sc=bpy.context.scene; sc.camera=cam
    sc.render.engine="BLENDER_EEVEE"
    sc.render.resolution_x=args.width; sc.render.resolution_y=args.height
    sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG"
    sc.render.filepath=args.out
    sc.view_settings.look="AgX - Medium High Contrast"

    blend=args.out.rsplit(".",1)[0]+".blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    bpy.ops.render.render(write_still=True)
    print("[AADWIK MAYA V3] FRAME:",args.out)
    print("[AADWIK MAYA V3] CHARACTER ID: char_maya_v3")
    print("[AADWIK MAYA V3] ASSET GATE COMPLETE")

if __name__=="__main__":
    main()
