AADWIK MASTER BATCH 33 — RENDER VERIFICATION REPAIR

This batch fixes the silent tiny-MP4 problem.
It keeps the animation pipeline local and free-first.

Installed files:
- app/renderer/local_video_provider.py
- app/renderer/aadwik_animation_scene.py

The scene is self-contained and renders 128 PNG frames:
8 shots × 2 seconds × 8 FPS = 128 frames.

Provider validation:
- captures Blender output
- rejects missing/partial PNG renders
- encodes with FFmpeg
- verifies MP4 duration/frame information with ffprobe
- rejects suspiciously small MP4s
- only returns success after validation

INSTALL FROM PROJECT ROOT:
C:\Users\olga_Ashok3\aadwik_mvp

Stop Uvicorn first, then:
Copy-Item .\AADWIK_MASTER_BATCH33\app\renderer\local_video_provider.py .\backend\app\providers\local_video_provider.py -Force
Copy-Item .\AADWIK_MASTER_BATCH33\app\renderer\aadwik_animation_scene.py .\backend\app\providers\aadwik_animation_scene.py -Force

Then start:
cd C:\Users\olga_Ashok3\aadwik_mvp\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Expected:
[AADWIK ANIMATION VERIFY] PNG frames: 128/128
[AADWIK ANIMATION VERIFY] MP4 duration: about 16 seconds
[AADWIK ANIMATION VERIFY] SUCCESS: ...

Do ONE test movie after installation.
