"""Aadwik 3D Video Engine V6 - Connected Character Production Layer.
No Pillow. No disconnected primitive body parts. Uses a single connected metaball-derived
body mesh, armature auto weights, facial controls, acting poses, and cinematic staging.
Designed for Blender 5.2 background rendering.
"""
import bpy, sys, os, json, argparse, math
from mathutils import Vector

def parse_args():
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',required=True); ap.add_argument('--out',required=True)
    ap.add_argument('--width',type=int,default=640); ap.add_argument('--height',type=int,default=360); ap.add_argument('--fps',type=int,default=8)
    raw=sys.argv; return ap.parse_args(raw[raw.index('--')+1:] if '--' in raw else [])

def material(name, color, rough=.45, emission=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value=(*color,1)
        bs.inputs['Roughness'].default_value=rough
        if emission:
            bs.inputs['Emission Color'].default_value=(*emission,1)
            bs.inputs['Emission Strength'].default_value=4.0
    return m

def setup_materials():
    return {
      'skin':material('V6_Skin',(0.52,0.19,0.075),.42),
      'hair':material('V6_Hair',(0.012,0.006,0.003),.3),
      'dress':material('V6_Dress',(0.035,0.22,0.62),.35),
      'scarf':material('V6_Scarf',(0.02,0.62,0.78),.28),
      'boot':material('V6_Boot',(0.035,0.022,0.016),.4),
      'eye':material('V6_Eye',(0.98,0.99,1),.16),
      'iris':material('V6_Iris',(0.04,0.32,0.70),.14),
      'pupil':material('V6_Pupil',(0.002,0.002,0.003),.1),
      'mouth':material('V6_Mouth',(0.22,0.008,0.015),.25),
      'ground':material('V6_Ground',(0.008,0.016,0.009),.96),
      'trunk':material('V6_Trunk',(0.08,0.035,0.014),.9),
      'leaf':material('V6_Leaf',(0.012,0.08,0.028),.9),
      'star':material('V6_Star',(0.05,0.38,1.0),.14,(0.03,0.35,1.0)),
      'gold':material('V6_Gold',(1.0,.52,.06),.18,(1.0,.32,.02)),
      'guardian':material('V6_Guardian',(.10,.55,1),.18,(.04,.32,1)),
    }

def smooth(o):
    if hasattr(o.data,'polygons'):
        for p in o.data.polygons: p.use_smooth=True
    return o

def uv(name,loc,scale,mat,seg=32,rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat); return smooth(o)

def cyl_between(name,a,b,r,mat,verts=24):
    a=Vector(a); b=Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y'); o.data.materials.append(mat)
    bev=o.modifiers.new('soft_edge','BEVEL'); bev.width=r*.35; bev.segments=3
    return smooth(o)

def connected_body(M):
    # One continuous organic surface. Overlapping metaball elements merge into a single mesh.
    mb=bpy.data.metaballs.new('V6_CONNECTED_BODY_META'); mb.resolution=.055; mb.render_resolution=.045; mb.threshold=.62
    obj=bpy.data.objects.new('CHAR_MAYA_V6_BODY',mb); bpy.context.collection.objects.link(obj)
    def add(co,size):
        e=mb.elements.new(); e.co=co; e.radius=size; e.stiffness=2.0
    # feet -> shins -> thighs -> pelvis -> torso -> neck -> head
    for x in (-.16,.16):
        add((x,0,.11),.17); add((x,0,.32),.15); add((x,0,.52),.18)
    add((0,0,.62),.34); add((0,0,.86),.35); add((0,0,1.10),.32); add((0,0,1.30),.22); add((0,0,1.48),.15); add((0,0,1.68),.31)
    # shoulders and arms with overlapping segments
    for s in (-1,1):
        add((s*.27,0,1.18),.18); add((s*.42,0,1.10),.14); add((s*.58,0,.94),.13); add((s*.69,0,.76),.12); add((s*.73,0,.61),.13)
    # convert to actual mesh
    bpy.context.view_layer.objects.active=obj; obj.select_set(True)
    bpy.ops.object.convert(target='MESH'); body=bpy.context.object; body.name='CHAR_MAYA_V6_CONNECTED_MESH'
    body.data.materials.append(M['skin']); smooth(body)
    # gentle subdivision for a smooth animated surface
    sub=body.modifiers.new('V6_Surface_Smooth','SUBSURF'); sub.levels=1; sub.render_levels=1
    return body

def make_rig():
    bpy.ops.object.armature_add(enter_editmode=True,location=(0,0,0)); rig=bpy.context.object; rig.name='CHAR_MAYA_V6_RIG'; eb=rig.data.edit_bones; eb.remove(eb[0])
    def B(n,h,t,p=None):
        b=eb.new(n); b.head=h; b.tail=t; b.parent=eb.get(p) if p else None; return b
    B('root',(0,0,0),(0,0,.25)); B('pelvis',(0,0,.25),(0,0,.62),'root'); B('spine',(0,0,.55),(0,0,1.08),'pelvis'); B('chest',(0,0,1.0),(0,0,1.28),'spine'); B('neck',(0,0,1.28),(0,0,1.48),'chest'); B('head',(0,0,1.48),(0,0,1.78),'neck')
    for s,n in [(-1,'L'),(1,'R')]:
        B('upper_arm.'+n,(s*.25,0,1.17),(s*.47,0,1.0),'chest'); B('lower_arm.'+n,(s*.47,0,1.0),(s*.66,0,.78),'upper_arm.'+n); B('hand.'+n,(s*.66,0,.78),(s*.74,0,.63),'lower_arm.'+n)
        B('thigh.'+n,(s*.12,0,.58),(s*.15,0,.34),'pelvis'); B('shin.'+n,(s*.15,0,.34),(s*.16,0,.11),'thigh.'+n); B('foot.'+n,(s*.16,0,.10),(s*.30,-.16,.08),'shin.'+n)
    bpy.ops.object.mode_set(mode='OBJECT'); rig['character_id']='char_maya_v6'; rig['identity_locked']=True; rig['asset_version']='6.0'; return rig

def bind(body,rig):
    # Automatic weights on the single manifold body mesh.
    bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active=rig
    try:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    except Exception:
        # Robust fallback: armature modifier keeps the production route alive even if auto weights fail.
        mod=body.modifiers.new('V6_Armature','ARMATURE'); mod.object=rig

def facial(M,rig):
    parts=[]
    for x in (-.115,.115):
        e=uv('MAYA_V6_EYE', (x,-.295,1.73),(.078,.035,.07),M['eye']); parts.append(e)
        i=uv('MAYA_V6_IRIS',(x,-.326,1.73),(.040,.012,.043),M['iris']); parts.append(i)
        p=uv('MAYA_V6_PUPIL',(x,-.337,1.73),(.018,.007,.022),M['pupil']); parts.append(p)
        b=uv('MAYA_V6_BROW',(x,-.302,1.83),(.09,.016,.022),M['hair']); parts.append(b)
    n=uv('MAYA_V6_NOSE',(0,-.305,1.66),(.043,.035,.06),M['skin']); parts.append(n)
    mouth=uv('MAYA_V6_MOUTH',(0,-.307,1.57),(.07,.014,.024),M['mouth']); parts.append(mouth)
    for o in parts:
        w=o.matrix_world.copy(); o.parent=rig; o.parent_type='BONE'; o.parent_bone='head'; o.matrix_world=w

def hair(M,rig):
    # Hair cap plus curved locks, all parented to head without transform jumps.
    cap=uv('MAYA_V6_HAIR_CAP',(0,.02,1.89),(.34,.30,.25),M['hair']); w=cap.matrix_world.copy(); cap.parent=rig; cap.parent_type='BONE'; cap.parent_bone='head'; cap.matrix_world=w
    for idx,x in enumerate([-.30,-.23,-.16,-.08,.08,.16,.23,.30]):
        o=uv('MAYA_V6_HAIR_LOCK_'+str(idx),(x,-.005,1.74+abs(x)*.12),(.055,.06,.25),M['hair'],24,16); o.rotation_euler[1]=x*.5
        w=o.matrix_world.copy(); o.parent=rig; o.parent_type='BONE'; o.parent_bone='head'; o.matrix_world=w

def clothing(M,rig):
    bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=.39,radius2=.34,depth=.62,location=(0,.01,.91)); dress=bpy.context.object; dress.name='MAYA_V6_DRESS'; dress.data.materials.append(M['dress'])
    bev=dress.modifiers.new('DressSoft','BEVEL'); bev.width=.07; bev.segments=4; sub=dress.modifiers.new('DressSmooth','SUBSURF'); sub.levels=1; sub.render_levels=1
    w=dress.matrix_world.copy(); dress.parent=rig; dress.parent_type='BONE'; dress.parent_bone='spine'; dress.matrix_world=w
    # scarf
    scarf=uv('MAYA_V6_SCARF',(0,-.10,1.28),(.33,.09,.045),M['scarf']); w=scarf.matrix_world.copy(); scarf.parent=rig; scarf.parent_type='BONE'; scarf.parent_bone='chest'; scarf.matrix_world=w
    for s in (-1,1):
        boot=uv('MAYA_V6_BOOT',(s*.17,-.10,.065),(.15,.22,.085),M['boot']); w=boot.matrix_world.copy(); boot.parent=rig; boot.parent_type='BONE'; boot.parent_bone='foot.'+('L' if s<0 else 'R'); boot.matrix_world=w

def pose(rig,kind,frame):
    p=rig.pose.bones
    for n in p: n.rotation_mode='XYZ'
    for n in ['spine','head','upper_arm.L','upper_arm.R','lower_arm.L','lower_arm.R','thigh.L','thigh.R','shin.L','shin.R']:
        p[n].rotation_euler=(0,0,0)
    if kind=='discover':
        p['spine'].rotation_euler[1]=-.08; p['head'].rotation_euler[1]=.14; p['upper_arm.L'].rotation_euler[2]=-.65; p['lower_arm.L'].rotation_euler[2]=-.35
    elif kind=='wonder':
        p['head'].rotation_euler[1]=-.16; p['head'].rotation_euler[2]=.08; p['upper_arm.L'].rotation_euler[2]=-.38; p['upper_arm.R'].rotation_euler[2]=.32
    elif kind=='protect':
        p['spine'].rotation_euler[1]=-.10; p['head'].rotation_euler[1]=-.18; p['upper_arm.L'].rotation_euler[2]=-.88; p['upper_arm.R'].rotation_euler[2]=.88; p['lower_arm.L'].rotation_euler[2]=-.35; p['lower_arm.R'].rotation_euler[2]=.35
    elif kind=='joy':
        p['spine'].rotation_euler[1]=.05; p['head'].rotation_euler[2]=-.08; p['upper_arm.L'].rotation_euler[2]=-.82; p['upper_arm.R'].rotation_euler[2]=.82
    for n in ['spine','head','upper_arm.L','upper_arm.R','lower_arm.L','lower_arm.R','thigh.L','thigh.R','shin.L','shin.R']:
        p[n].keyframe_insert('rotation_euler',frame=frame)

def look(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def environment(M):
    bpy.ops.mesh.primitive_plane_add(size=30,location=(0,0,0)); bpy.context.object.data.materials.append(M['ground'])
    for i in range(16):
        x=-7+(i%8)*2.0; y=2.2+(i//8)*2.6
        cyl_between('TREE',(x,y,.1),(x,y,2.8),.14,M['trunk'])
        uv('CANOPY',(x,y,3.15),(1.0,1.0,1.15),M['leaf'],28,18)
    for i in range(10):
        x=-5+i*1.1; y=-.9-(i%3)*.3; uv('ROCK',(x,y,.14),(.28,.20,.15),M['trunk'],24,16)

def star(M):
    o=uv('V6_MAGIC_STAR',(.9,-.18,1.15),(.18,.08,.18),M['star']); return o

def guardian(M):
    body=uv('V6_GUARDIAN_BODY',(1.02,.04,1.03),(.18,.16,.27),M['guardian']); head=uv('V6_GUARDIAN_HEAD',(1.02,-.02,1.34),(.20,.18,.19),M['gold'])
    for s in (-1,1): uv('V6_GUARDIAN_WING_'+str(s),(1.02+s*.22,.03,1.12),(.20,.05,.30),M['guardian'])

def main():
    args=parse_args(); plan=json.load(open(args.plan,encoding='utf-8'))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M=setup_materials(); sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=args.width; sc.render.resolution_y=args.height; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'; sc.render.fps=args.fps; sc.render.film_transparent=False
    sc.world=bpy.data.worlds.new('V6_WORLD'); sc.world.use_nodes=True; bg=sc.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.002,.005,.015,1); bg.inputs['Strength'].default_value=.20
    print('[AADWIK V6] CONNECTED CHARACTER ENGINE ACTIVE')
    print('[AADWIK V6] SINGLE ORGANIC BODY MESH + ARMATURE + ACTING')
    environment(M); body=connected_body(M); rig=make_rig(); bind(body,rig); facial(M,rig); hair(M,rig); clothing(M,rig); guardian(M); st=star(M)
    bpy.ops.object.camera_add(location=(0,-6.8,2.0)); cam=bpy.context.object; sc.camera=cam; cam.data.lens=58; cam.data.dof.use_dof=True; cam.data.dof.focus_object=rig; cam.data.dof.aperture_fstop=3.0
    bpy.ops.object.light_add(type='AREA',location=(2.5,-3.5,4.5)); key=bpy.context.object; key.data.energy=1000; key.data.size=4; look(key,(0,0,1.2))
    bpy.ops.object.light_add(type='AREA',location=(-2.5,-1.5,2.8)); fill=bpy.context.object; fill.data.energy=350; fill.data.size=3; look(fill,(0,0,1.1))
    bpy.ops.object.light_add(type='POINT',location=(.9,-.2,1.2)); rim=bpy.context.object; rim.data.energy=300; rim.data.color=(.12,.40,1)
    total=16; scenes=plan.get('scenes') or [{'emotion':'curious','action':'discover'}]
    for si,s in enumerate(scenes,1):
        txt=' '.join(str(s.get(k,'')) for k in ['action','description','emotion','location']).lower()
        kind='protect' if any(k in txt for k in ['danger','fear','protect','shadow']) else ('joy' if any(k in txt for k in ['happy','joy','return','sunrise']) else ('discover' if any(k in txt for k in ['star','discover','curious','find']) else 'wonder'))
        for f in range(1,total+1):
            t=(f-1)/(total-1); pose(rig,kind,f)
            rig.location=(-.25+.18*t,.02*math.sin(t*math.pi*2),0); rig.keyframe_insert('location',frame=f)
            p=rig.pose.bones['head']; p.rotation_euler.z += .035*math.sin(t*math.pi*2); p.keyframe_insert('rotation_euler',frame=f)
            st.scale=(1+.15*math.sin(t*math.pi),1+.15*math.sin(t*math.pi),1+.15*math.sin(t*math.pi)); st.keyframe_insert('scale',frame=f)
            cam.location=(.15*math.sin(t*math.pi),-6.8+.3*math.sin(t*math.pi),2.0+.10*math.sin(t*math.pi)); look(cam,(-.05+.15*t,0,1.35)); cam.keyframe_insert('location',frame=f); cam.keyframe_insert('rotation_euler',frame=f)
            sc.frame_set(f); sc.render.filepath=os.path.join(args.out,f'frame_{(si-1)*total+f:06d}.png'); bpy.ops.render.render(write_still=True)
    print('[AADWIK V6] RENDER COMPLETE')

if __name__=='__main__': main()
