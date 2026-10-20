import bpy
from mathutils import Vector

for o in bpy.data.objects:
    if o.type == 'MESH' and any(k in o.name.lower() for k in ['eye', 'iris', 'pupil']):
        bpy.context.view_layer.update()
        corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
        mn = [min(v[i] for v in corners) for i in range(3)]
        mx = [max(v[i] for v in corners) for i in range(3)]
        print(o.name, 'center=', tuple(round((mn[i]+mx[i])/2,4) for i in range(3)),
              'size=', tuple(round(mx[i]-mn[i],4) for i in range(3)))
