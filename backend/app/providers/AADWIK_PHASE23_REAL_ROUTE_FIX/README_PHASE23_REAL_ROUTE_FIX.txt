AADWIK PHASE 23 — REAL MOVIE ROUTE INTEGRATION FIX

Purpose
-------
The real movie-generation route was successfully rendering PNGs and encoding
MP4s, but it was still selecting the legacy Pillow/procedural character scene.
This patch makes LocalVideoProvider explicitly launch the Phase 23 cinematic
Blender scene and pass it a controlled production plan.

Replace these files in:
C:\Users\olga_Ashok3\aadwik_mvp\backend\app\providers\

1) local_video_provider.py
2) aadwik_blender_scene.py
3) aadwik_character_quality.py

IMPORTANT
---------
Do not leave an older aadwik_blender_scene.py in the providers folder.
The provider now resolves the scene script directly beside itself.

Validation
----------
From backend:

python -m py_compile app\providers\local_video_provider.py app\providers\aadwik_blender_scene.py app\providers\aadwik_character_quality.py
python tests\test_phase23_real_route.py

Expected:
PHASE 23 REAL ROUTE INTEGRATION: PASS
Legacy Pillow scene is not selected by LocalVideoProvider.
Explicit Phase 23 --plan handoff: PASS

Then restart backend:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

The next movie generation should log:
[AADWIK] Phase 23 scene: ...\\app\\providers\\aadwik_blender_scene.py
[AADWIK] Phase 23 character library: ...\\app\\providers\\aadwik_character_quality.py
[AADWIK] Production plan: ...phase23_production_plan.json
[AADWIK 23] SCENE ...

The old Pillow renderer must not appear in the movie-generation log.
