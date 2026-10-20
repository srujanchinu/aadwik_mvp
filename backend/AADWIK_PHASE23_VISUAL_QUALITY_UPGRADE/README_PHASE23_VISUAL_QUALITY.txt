
AADWIK PHASE 23 - VISUAL QUALITY UPGRADE

Purpose:
Replace the current low-poly/Pillow-looking character appearance with a
smoother cinematic-stylized 3D character layer while preserving the real
movie route interfaces.

Replace:
backend\app\providers\aadwik_character_quality.py
backend\app\providers\aadwik_blender_scene.py

Do not replace local_video_provider.py. The current real route already
points to the correct Phase 23 scene and character library.

Validation:
python tests\test_phase23_visual_quality.py
python -m py_compile app\providers\aadwik_character_quality.py app\providers\aadwik_blender_scene.py

Then restart Uvicorn and generate the same forest/star test movie.

Expected:
- smoother rounded character silhouettes
- more readable face with eyes/iris/pupils/brows/mouth
- layered clothing and hair
- better moon key + warm face fill + blue rim/practical
- less obstructive forest framing
- same 640x360 / 8 FPS development settings
