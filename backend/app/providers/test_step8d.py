import runpy, bpy
runpy.run_path("aadwik_asset_injector.py")

expected=[
"char_tara_v1","char_guardian_v1",
"char_shadow_creature_v1","prop_blue_star_v1"
]
for aid in expected:
    col=bpy.data.collections.get("SHOT_ASSET_"+aid)
    assert col is not None, aid
    assert len(col.objects) > 0, aid
    print(aid, "ACTUAL BLENDER ASSET OK", len(col.objects), "objects")

assert bpy.data.filepath.endswith("step8d_injected_assets.blend")
print("BLENDER INJECTION: OK")
print("REUSABLE ASSETS: OK")
print("STEP 8D PASS")
