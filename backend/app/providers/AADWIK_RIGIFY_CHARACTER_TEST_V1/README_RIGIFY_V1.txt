
AADWIK RIGIFY CHARACTER TEST V1
================================

Purpose
-------
Test the correct Blender character workflow before touching Aadwik's movie
pipeline:

Maya V3 character
-> Human Rigify metarig
-> Rigify generated rig
-> automatic skinning
-> simple control pose
-> diagnostic render

This package intentionally does NOT modify:
- local_video_provider.py
- movie_service
- FFmpeg movie pipeline
- Story Engine
- production planner

Requirements
------------
Blender 5.2.x
Rigify bundled with Blender.

IMPORTANT
---------
The script runs the existing Maya V3 builder first. It then creates the
Rigify human metarig and generates the production rig.

The official Rigify workflow requires the metarig bones to be positioned to
match the character before generation. This V1 script establishes the
pipeline and creates a diagnostic checkpoint; it is not being presented as
final automatic bone fitting.

Outputs
-------
<Maya V3 script directory> / generated:
- AADWIK_RIGIFY_V1_METARIG.blend
- AADWIK_RIGIFY_V1.blend
- aadwik_rigify_v1.png

Recommended test
----------------
Run from PowerShell after extracting this package:

& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P `
"C:\Users\olga_Ashok3\aadwik_mvp\backend\app\providers\AADWIK_RIGIFY_CHARACTER_TEST_V1\blender\aadwik_rigify_character_test_v1.py" -- `
--source `
"C:\Users\olga_Ashok3\aadwik_mvp\backend\app\providers\AADWIK_MAYA_CHARACTER_V3\blender\aadwik_maya_character_v3.py" `
--blend_out `
"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_rigify_v1.blend" `
--render_out `
"C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_rigify_v1.png" `
--width 640 --height 640

Then inspect:
C:\Users\olga_Ashok3\aadwik_mvp\backend\generated\aadwik_rigify_v1.png

If Rigify generation fails, do not change the movie pipeline. Upload the
Blender console output so the metarig/generation step can be corrected.
