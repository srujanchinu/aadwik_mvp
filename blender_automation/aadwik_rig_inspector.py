import bpy

print("\n" + "=" * 70)
print("AADWIK CHARACTER / DEFORMATION AUDIT")
print("=" * 70)

rig = bpy.data.objects.get("Aadwik_Main_Rig")

if not rig:
    print("ERROR: Aadwik_Main_Rig not found.")
    raise SystemExit

print(f"\nRIG: {rig.name}")
print(f"Pose bones: {len(rig.pose.bones)}")

print("\n" + "-" * 70)
print("MESH OBJECTS")
print("-" * 70)

meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]

for obj in meshes:
    print(f"\n[{obj.name}]")
    print(f"  Vertices: {len(obj.data.vertices)}")
    print(f"  Polygons: {len(obj.data.polygons)}")
    print(f"  Vertex Groups: {len(obj.vertex_groups)}")

    armature_modifiers = []

    for mod in obj.modifiers:
        if mod.type == "ARMATURE":
            armature_modifiers.append(mod)

    if not armature_modifiers:
        print("  Armature Modifier: NONE")
    else:
        for mod in armature_modifiers:
            target = mod.object.name if mod.object else "NONE"
            print(f"  Armature Modifier: {mod.name}")
            print(f"    Target: {target}")

    # Check whether useful rig bone groups exist
    important_groups = [
        "DEF-upper_arm.L",
        "DEF-forearm.L",
        "DEF-hand.L",
        "DEF-thigh.L",
        "DEF-shin.L",
        "DEF-foot.L",
    ]

    found = []
    for group in important_groups:
        if obj.vertex_groups.get(group):
            found.append(group)

    if found:
        print("  Important DEF groups found:")
        for group in found:
            print(f"    + {group}")
    else:
        print("  Important DEF groups: NONE FOUND")

print("\n" + "-" * 70)
print("RIGGED MESH SUMMARY")
print("-" * 70)

rigged = 0
unrigged = 0

for obj in meshes:
    has_rig = any(
        mod.type == "ARMATURE" and mod.object == rig
        for mod in obj.modifiers
    )

    if has_rig:
        print(f"[RIGGED]   {obj.name}")
        rigged += 1
    else:
        print(f"[NOT RIGGED] {obj.name}")
        unrigged += 1

print(f"\nRigged meshes: {rigged}")
print(f"Non-rigged meshes: {unrigged}")

print("\n" + "=" * 70)
print("CHARACTER AUDIT COMPLETE")
print("=" * 70)