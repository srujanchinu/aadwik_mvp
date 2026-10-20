import bpy, sys, os, math, argparse
from mathutils import Vector

def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for d in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        pass

def mat(name, color, emission=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value=(*color,1)
        bs.inputs["Roughness"].default_value=.55
        if emission:
            bs.inputs["Emission Color"].default_value=(*color,1)
            bs.inputs["Emission Strength"].default_value=emission
    return m

SKIN=mat("Tara Skin",(0.78,.42,.25))
HAIR=mat("Tara Hair",(.08,.035,.018))
SHIRT=mat("Tara Shirt",(.12,.28,.65))
PANTS=mat("Tara Pants",(.06,.08,.16))
SHOE=mat("Shoes",(.03,.03,.04))
WHITE=mat("Eyes",(.95,.95,.95))
BLACK=mat("Pupils",(.01,.01,.01))
GUARD=mat("Guardian",(.28,.65,.82),.15)
STAR=mat("Blue Star",(0.05,.35,1.0),3.0)
TREE=mat("Trees",(.055,.16,.08))
GROUND=mat("Ground",(.025,.055,.035))
MOON=mat("Moon",(.8,.85,1),1.5)

def cube(name, loc, scale, material, bevel=.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new("Soft","BEVEL"); mod.width=bevel; mod.segments=3
    o.data.materials.append(material); return o

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material); return o

def cyl(name, loc, radius, depth, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material); return o

def limb(name, a, b, radius, material):
    a,b=Vector(a),Vector(b); d=b-a
    o=cyl(name,(a+b)/2,radius,d.length,material)
    o.rotation_mode="QUATERNION"; o.rotation_quaternion=d.to_track_quat("Z","Y")
    return o

def tara():
    root=bpy.data.objects.new("Tara",None); bpy.context.collection.objects.link(root)
    parts=[]
    parts.append(sphere("TaraHead",(0,0,2.35),(.42,.38,.46),SKIN))
    parts.append(sphere("TaraHair",(0,.02,2.62),(.45,.40,.28),HAIR))
    for x in (-.15,.15):
        parts.append(sphere("TaraEye",(x,-.355,2.42),(.075,.035,.09),WHITE))
        parts.append(sphere("TaraPupil",(x,-.39,2.42),(.032,.018,.045),BLACK))
    parts.append(cube("TaraBody",(0,0,1.72),(.32,.20,.48),SHIRT,.08))
    parts += [limb("TaraArmL",(-.3,0,2.02),(-.58,0,1.55),.09,SKIN),
              limb("TaraArmR",(.3,0,2.02),(.58,0,1.55),.09,SKIN)]
    parts += [limb("TaraLegL",(-.14,0,1.25),(-.22,0,.62),.115,PANTS),
              limb("TaraLegR",(.14,0,1.25),(.22,0,.62),.115,PANTS)]
    parts += [sphere("TaraShoeL",(-.22,-.08,.55),(.16,.24,.09),SHOE),
              sphere("TaraShoeR",(.22,-.08,.55),(.16,.24,.09),SHOE)]
    for p in parts: p.parent=root
    return root

def guardian():
    root=bpy.data.objects.new("Guardian",None); bpy.context.collection.objects.link(root)
    body=sphere("GuardianBody",(0,0,1.1),(.25,.22,.32),GUARD); body.parent=root
    for x in (-.09,.09):
        sphere("GuardianEye",(x,-.205,1.18),(.045,.025,.055),WHITE).parent=root
    for x in (-.32,.32):
        limb("GuardianWing",(0,0,1.15),(x,0,1.3),.055,GUARD).parent=root
    return root

def forest():
    cube("Ground",(0,0,0), (8,8,.08),GROUND)
    for x in (-6,-4,-2,2,4,6):
        for y in (2,5,-3):
            trunk=cyl("TreeTrunk",(x,y,1.4),.18,2.8,TREE)
            sphere("TreeCrown",(x,y,3.0),(1.0,1.0,1.3),TREE)

def blue_star():
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.22,location=(0,0,2.1))
    o=bpy.context.object; o.name="BlueStar"; o.data.materials.append(STAR)
    return o

def camera_setup():
    bpy.ops.object.camera_add(location=(5,-8,4))
    cam=bpy.context.object; cam.name="AadwikCamera"; bpy.context.scene.camera=cam
    return cam

def look_at(cam, target):
    direction=Vector(target)-cam.location
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()

def animate(root, start, end, x0, x1):
    root.location=(x0,0,0); root.keyframe_insert("location",frame=start,index=0)
    root.location=(x1,0,0); root.keyframe_insert("location",frame=end,index=0)
    for fc in root.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation="BEZIER"

def main():
    argv=sys.argv
    if "--" in argv: argv=argv[argv.index("--")+1:]
    ap=argparse.ArgumentParser()
    ap.add_argument("--frames_dir",required=True); ap.add_argument("--width",type=int,default=640)
    ap.add_argument("--height",type=int,default=360); ap.add_argument("--fps",type=int,default=8)
    ap.add_argument("--prompt",default="")
    args=ap.parse_args(argv)

    clear()
    s=bpy.context.scene
    s.render.engine="BLENDER_EEVEE"
    s.render.resolution_x=args.width; s.render.resolution_y=args.height
    s.render.resolution_percentage=100; s.render.fps=args.fps
    s.render.image_settings.file_format="PNG"
    s.render.film_transparent=False
    s.world.color=(.008,.012,.025)

    forest(); tara(); g=guardian(); star=blue_star(); cam=camera_setup()
    # Keyframe the three important story subjects.
    animate(bpy.data.objects["Tara"],1,128,-2.2,2.2)
    g.location=(1.2,0,0); g.keyframe_insert("location",frame=1)
    g.location=(1.2,0,.45); g.keyframe_insert("location",frame=64)
    g.location=(.3,0,.1); g.keyframe_insert("location",frame=128)
    star.location=(0,0,2.0); star.keyframe_insert("location",frame=1)
    star.location=(0,0,2.5); star.keyframe_insert("location",frame=64)
    star.location=(0,0,2.1); star.keyframe_insert("location",frame=128)

    # Simple moon/key light.
    bpy.ops.object.light_add(type="AREA", location=(0,-3,7))
    key=bpy.context.object; key.name="MoonLight"; key.data.energy=900; key.data.shape="DISK"; key.data.size=5
    key.data.color=(.55,.65,1.0)

    os.makedirs(args.frames_dir,exist_ok=True)
    # Eight two-second shots, 16 frames each = 128 frames.
    for shot in range(8):
        start=shot*16+1; end=(shot+1)*16
        for f in range(start,end+1):
            s.frame_set(f)
            t=(f-start)/16.0
            if shot==0: cam.location=(5-2*t,-8,4)
            elif shot==1: cam.location=(2,-7,3.2+1*t)
            elif shot==2: cam.location=(0,-6,3.0)
            elif shot==3: cam.location=(-2+2*t,-6,3.2)
            elif shot==4: cam.location=(3,-5,2.8)
            elif shot==5: cam.location=(0,-5,4.2)
            elif shot==6: cam.location=(-3,-6,3.4)
            else: cam.location=(1,-8,3.8)
            look_at(cam,(0,0,1.8))
            s.render.filepath=os.path.join(args.frames_dir,f"shot_{shot+1:02d}_{f:04d}.png")
            bpy.ops.render.render(write_still=True)

if __name__=="__main__":
    main()
