# FAST Aadwik hair mesh visual inspector. Diagnostic only; never saves the source blend.
import bpy, sys, os, math
from mathutils import Vector

def arg_value(flag, default):
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    try: return args[args.index(flag) + 1]
    except (ValueError, IndexError): return default

source = os.path.abspath(arg_value('--source', 'generated/aadwik_character_master_v4_sportsuit_fix.blend'))
out_path = os.path.abspath(arg_value('--out', 'generated/reports/aadwik_hair_mesh_visual_inspector.png'))
if not os.path.isfile(source): raise FileNotFoundError('Blend file not found: ' + source)
print('AADWIK_FAST_HAIR_INSPECTOR: opening source', flush=True)
bpy.ops.wm.open_mainfile(filepath=source)
scene = bpy.context.scene
hair = bpy.data.objects.get('Human.bob01')
if not hair or hair.type != 'MESH': raise RuntimeError('Hair mesh Human.bob01 not found')
for obj in bpy.data.objects:
    if obj.name.startswith('WGT-'): obj.hide_render = True
coords = [hair.matrix_world @ v.co for v in hair.data.vertices]
lo = Vector(tuple(min(p[i] for p in coords) for i in range(3)))
hi = Vector(tuple(max(p[i] for p in coords) for i in range(3)))
center = (lo + hi) * .5
span = max(*(hi[i]-lo[i] for i in range(3)), .05)
created = []
def aim(obj, target): obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def light(name, pos, energy, size):
    d=bpy.data.lights.new(name,'AREA'); d.energy=energy; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=pos; aim(o,center); created.append(o)
light('AADWIK_FAST_KEY',center+Vector((-span*1.8,-span*2.4,span*1.6)),450,span*1.2)
light('AADWIK_FAST_FILL',center+Vector((span*1.8,-span*2.2,span*.8)),220,span)
cd=bpy.data.cameras.new('AADWIK_FAST_CAMERA'); cd.type='ORTHO'; cd.ortho_scale=span*1.65
cam=bpy.data.objects.new('AADWIK_FAST_CAMERA',cd); scene.collection.objects.link(cam); cam.location=center+Vector((0,-span*3.5,span*.2)); aim(cam,center); scene.camera=cam; created.append(cam)
# Count incident faces to identify open/boundary edges.
counts=[0]*len(hair.data.vertices)
for poly in hair.data.polygons:
    for vi in poly.vertices: counts[vi]+=1
boundary=[v.index for v in hair.data.vertices if counts[v.index] <= 2]
# Limit to at most 350 boundary points and 250 interior points; create ONE marker mesh.
if len(boundary)>350:
    step=math.ceil(len(boundary)/350); boundary=boundary[::step]
interior=[v.index for v in hair.data.vertices if counts[v.index]>2]
if len(interior)>250:
    step=math.ceil(len(interior)/250); interior=interior[::step]
verts=[]; faces=[]; mat_ids=[]; radius=span*.006
# Octahedron marker geometry, combined into one object to avoid thousands of Blender operators.
def add_octa(pos, r, material_index):
    base=len(verts)
    verts.extend([(pos.x+r,pos.y,pos.z),(pos.x-r,pos.y,pos.z),(pos.x,pos.y+r,pos.z),(pos.x,pos.y-r,pos.z),(pos.x,pos.y,pos.z+r),(pos.x,pos.y,pos.z-r)])
    local=[(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)]
    for f in local: faces.append(tuple(base+i for i in f)); mat_ids.append(material_index)
for idx in boundary: add_octa(coords[idx],radius*1.3,0)
for idx in interior: add_octa(coords[idx],radius*.75,1)
md=bpy.data.meshes.new('AADWIK_FAST_MARKERS_MESH'); md.from_pydata(verts,[],faces); md.update()
mo=bpy.data.objects.new('AADWIK_FAST_MARKERS',md); scene.collection.objects.link(mo); created.append(mo)
def mat(name,color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value=(*color,1)
        if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value=(*color,1); bs.inputs['Emission Strength'].default_value=1
    return m
mo.data.materials.append(mat('AADWIK_FAST_BOUNDARY',(1,.12,.015)))
mo.data.materials.append(mat('AADWIK_FAST_INTERIOR',(.02,.8,1)))
for p,mi in zip(md.polygons,mat_ids): p.material_index=mi
old_path=scene.render.filepath; old_res=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage); old_format=scene.render.image_settings.file_format; old_exposure=scene.view_settings.exposure
try:
    scene.render.resolution_x=800; scene.render.resolution_y=800; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.view_settings.exposure=-.5; scene.render.filepath=out_path
    os.makedirs(os.path.dirname(out_path),exist_ok=True)
    print('AADWIK_FAST_HAIR_INSPECTOR: rendering one combined marker mesh',flush=True)
    bpy.ops.render.render(write_still=True)
    print('AADWIK_FAST_HAIR_INSPECTION_COMPLETE',flush=True); print('Image:',out_path,flush=True)
    print('Red/orange = sampled boundary vertices; cyan = sampled interior vertices.',flush=True)
    print('Source blend was not saved or modified.',flush=True)
finally:
    scene.render.filepath=old_path; scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=old_res; scene.render.image_settings.file_format=old_format; scene.view_settings.exposure=old_exposure
