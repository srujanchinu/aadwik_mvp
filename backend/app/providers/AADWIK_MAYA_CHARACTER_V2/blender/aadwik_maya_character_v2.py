
import bpy, sys, math, argparse
from mathutils import Vector

print("[AADWIK MAYA V2] PROPER STYLIZED CHARACTER ASSET")

def material(name, color, rough=.42, metallic=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value=(*color,1)
        bs.inputs["Roughness"].default_value=rough
        bs.inputs["Metallic"].default_value=metallic
    return m

def uv(name, loc, scale, mat, seg=48, rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth=True
    return o

def capsule(name,a,b,r,mat):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=d.length, location=(a+b)/2)
    o=bpy.context.object; o.name=name
    o.rotation_mode="QUATERNION"; o.rotation_quaternion=d.to_track_quat("Z","Y")
    o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth=True
    bev=o.modifiers.new("Soft_Round","BEVEL"); bev.width=r*.72; bev.segments=4
    return o

def build_body(skin):
    # Deliberately human-like proportions: head, torso, upper/lower limbs.
    parts=[]
    parts.append(uv("MAYA_TORSO",(0,0,2.65),(.66,.46,.92),skin))
    parts.append(uv("MAYA_PELVIS",(0,0,1.78),(.58,.44,.42),skin))
    parts.append(uv("MAYA_HEAD",(0,0,4.22),(.56,.49,.62),skin))
    # neck
    parts.append(capsule("MAYA_NECK",(0,0,3.52),(0,0,3.78),.23,skin))
    # arms with elbow definition
    for side,x in (("L",-1),("R",1)):
        sx=.60*x
        parts += [
            capsule("MAYA_UPPER_ARM_"+side,(sx,0,3.15),(.88*x,-.01,2.55),.20,skin),
            capsule("MAYA_FOREARM_"+side,(.88*x,-.01,2.55),(.92*x,-.08,1.98),.17,skin),
            uv("MAYA_HAND_"+side,(.92*x,-.09,1.82),(.22,.19,.27),skin),
        ]
    # legs
    for side,x in (("L",-1),("R",1)):
        sx=.29*x
        parts += [
            capsule("MAYA_THIGH_"+side,(sx,0,1.65),(sx*1.08,0,.88),.27,skin),
            capsule("MAYA_SHIN_"+side,(sx*1.08,0,.88),(sx*1.08,-.02,.28),.21,skin),
        ]
    return parts

def build_face(skin, hair, eye, iris, black, dress, scarf, shoe):
    # Head is already a smooth base; facial pieces sit naturally on the front.
    for x in (-.19,.19):
        uv("MAYA_EYE",(x,-.455,4.30),(.115,.055,.14),eye)
        uv("MAYA_IRIS",(x,-.505,4.30),(.055,.018,.068),iris)
        uv("MAYA_PUPIL",(x,-.525,4.30),(.025,.009,.034),black)
        b=uv("MAYA_BROW",(x,-.47,4.48),(.105,.018,.035),black,32,16)
        b.rotation_euler[1]=(-.08 if x<0 else .08)
    uv("MAYA_NOSE",(0,-.50,4.10),(.045,.05,.075),skin,32,20)
    uv("MAYA_MOUTH",(0,-.51,3.96),(.12,.018,.035),black,32,16)

    # Hair: cap plus tapered side locks, kept smaller than the head.
    uv("MAYA_HAIR_CAP",(0,.01,4.54),(.57,.49,.38),hair)
    uv("MAYA_HAIR_L",(-.47,.00,4.25),(.16,.22,.55),hair)
    uv("MAYA_HAIR_R",(.47,.00,4.25),(.16,.22,.55),hair)

    # Fitted dress shell, not a giant oval.
    uv("MAYA_DRESS",(0,.005,2.62),(.69,.48,.88),dress)
    # scarf
    uv("MAYA_SCARF",(0,-.46,3.62),(.39,.055,.10),scarf,40,20)
    # shoes
    uv("MAYA_SHOE_L",(-.30,-.10,.14),(.30,.45,.15),shoe)
    uv("MAYA_SHOE_R",(.30,-.10,.14),(.30,.45,.15),shoe)

def build_rig():
    bpy.ops.object.armature_add(location=(0,0,.15))
    rig=bpy.context.object; rig.name="MAYA_RIG_V2"
    rig.show_in_front=True
    bpy.ops.object.mode_set(mode="EDIT")
    a=rig.data.edit_bones[0]; a.name="root"; a.head=(0,0,.1); a.tail=(0,0,1)
    spine=rig.data.edit_bones.new("spine"); spine.head=(0,0,1); spine.tail=(0,0,3.4); spine.parent=a
    neck=rig.data.edit_bones.new("neck"); neck.head=(0,0,3.4); neck.tail=(0,0,3.9); neck.parent=spine
    head=rig.data.edit_bones.new("head"); head.head=(0,0,3.9); head.tail=(0,0,4.75); head.parent=neck
    for side,x in (("L",-1),("R",1)):
        u=rig.data.edit_bones.new("upper_arm_"+side); u.head=(.58*x,0,3.15); u.tail=(.88*x,0,2.55); u.parent=spine
        f=rig.data.edit_bones.new("forearm_"+side); f.head=(.88*x,0,2.55); f.tail=(.92*x,0,1.95); f.parent=u
        h=rig.data.edit_bones.new("hand_"+side); h.head=(.92*x,0,1.95); h.tail=(.92*x,0,1.65); h.parent=f
        t=rig.data.edit_bones.new("thigh_"+side); t.head=(.29*x,0,1.7); t.tail=(.31*x,0,.9); t.parent=spine
        s=rig.data.edit_bones.new("shin_"+side); s.head=(.31*x,0,.9); s.tail=(.31*x,0,.3); s.parent=t
        ft=rig.data.edit_bones.new("foot_"+side); ft.head=(.31*x,0,.3); ft.tail=(.31*x,-.3,.15); ft.parent=s
    bpy.ops.object.mode_set(mode="OBJECT")
    rig["character_id"]="char_maya_v2"
    rig["identity_locked"]=True
    rig["asset_type"]="reusable_stylized_3d_character"
    return rig

def main():
    argv=sys.argv
    if "--" in argv: argv=argv[argv.index("--")+1:]
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); ap.add_argument("--width",type=int,default=640); ap.add_argument("--height",type=int,default=640)
    args=ap.parse_args(argv)
    bpy.ops.wm.read_factory_settings(use_empty=True)

    skin=material("MayaSkin",(0.58,0.24,0.12),.48)
    hair=material("MayaHair",(0.018,0.008,0.004),.34)
    eye=material("MayaEye",(0.97,.97,.93),.2)
    iris=material("MayaIris",(0.03,.22,.48),.22)
    black=material("MayaBlack",(.004,.003,.003),.24)
    dress=material("MayaDress",(.08,.25,.68),.38)
    scarf=material("MayaScarf",(.02,.63,.82),.3)
    shoe=material("MayaShoe",(.025,.035,.06),.38)

    body=build_body(skin)
    build_face(skin,hair,eye,iris,black,dress,scarf,shoe)
    rig=build_rig()
    rig.hide_viewport=True; rig.hide_render=True

    # Studio floor/world.
    ground=material("StudioFloor",(.035,.045,.065),.68)
    bpy.ops.mesh.primitive_plane_add(size=25,location=(0,0,0)); bpy.context.object.data.materials.append(ground)
    world=bpy.data.worlds.new("AADWIK_WORLD"); bpy.context.scene.world=world; world.color=(.006,.009,.018)

    for name,loc,energy,size in [
        ("Key",(-4,-6,7),1100,4.0),("Fill",(4,-5,5),650,3.5),("Rim",(0,3,7),1300,3.0)]:
        bpy.ops.object.light_add(type="AREA",location=loc)
        l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.shape="DISK"; l.data.size=size
        l.rotation_euler=(Vector((0,0,2.7))-l.location).to_track_quat("-Z","Y").to_euler()

    bpy.ops.object.camera_add(location=(0,-11,3.0))
    cam=bpy.context.object; cam.data.lens=58
    cam.rotation_euler=(Vector((0,0,2.65))-cam.location).to_track_quat("-Z","Y").to_euler()
    sc=bpy.context.scene; sc.camera=cam
    sc.render.engine="BLENDER_EEVEE"
    sc.render.resolution_x=args.width; sc.render.resolution_y=args.height; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG"; sc.render.filepath=args.out
    sc.view_settings.look="AgX - Medium High Contrast"
    bpy.ops.wm.save_as_mainfile(filepath=args.out.rsplit(".",1)[0]+".blend")
    bpy.ops.render.render(write_still=True)
    print("[AADWIK MAYA V2] FRAME:",args.out)
    print("[AADWIK MAYA V2] CHARACTER ID: char_maya_v2")

if __name__=="__main__": main()
