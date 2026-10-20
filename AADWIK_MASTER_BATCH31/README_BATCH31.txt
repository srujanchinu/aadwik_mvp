AADWIK MASTER BATCH 31
Story-Aware Stylized 3D Cartoon Renderer

Purpose:
Replace the primitive Phase-23 scene output with a self-contained, story-aware
stylized 3D cartoon renderer for the current local Blender pipeline.

Current smoke-test story:
A curious girl discovers a glowing blue star in a moonlit forest and helps a tiny guardian return home.

What changes:
- Proper modeled Tara: face, eyes/pupils, hair, clothing, limbs, backpack.
- Tiny Guardian with face and expressive silhouette.
- Glowing blue star and halos.
- Moonlit forest with trees, shrubs, path, moon and stars.
- 8 cinematic shots with camera movement.
- Character motion and continuity.
- Prompt is forwarded from the backend provider to Blender.
- PNG discovery is recursive and robust.
- Existing Blender/FFmpeg executables are untouched.
- Installer backs up existing live files before replacement.

Install from:
C:\Users\olga_Ashok3\aadwik_mvp

Test:
python .\AADWIK_MASTER_BATCH31\tests\test_master_batch31.py

Install:
python .\AADWIK_MASTER_BATCH31\tools\install_batch31.py

Then restart backend and create the same one-line test story.
