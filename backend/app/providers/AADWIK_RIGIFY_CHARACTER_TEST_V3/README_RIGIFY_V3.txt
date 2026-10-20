AADWIK RIGIFY CHARACTER TEST V3
Fixes V2 argparse problem. Loads only the Maya V3 builder portion, then creates and saves a Human Meta-Rig. Generation is intentionally stopped so the metarig can be fitted to the character before Rigify generation.

Run:
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P "C:\Users\olga_Ashok3\aadwik_mvp\backend\app\providers\AADWIK_RIGIFY_CHARACTER_TEST_V3\blender\aadwik_rigify_character_test_v3.py" -- --source "C:\Users\olga_Ashok3\aadwik_mvp\backend\app\providers\aadwik_maya_character_v3.py" --blend_out "C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_rigify_v3.blend" --width 640 --height 640
