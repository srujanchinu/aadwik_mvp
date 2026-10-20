import bpy, runpy
runpy.run_path("aadwik_character_asset_builder.py")
names = ["CHAR_TARA_ROOT","CHAR_GUARDIAN_ROOT","CHAR_SHADOW_ROOT","PROP_BLUE_STAR"]
for n in names:
    print(n, "OK" if bpy.data.objects.get(n) else "MISSING")
