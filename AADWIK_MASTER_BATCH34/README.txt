AADWIK MASTER BATCH 34
Provider Assembly Integration

Purpose:
- Keep the verified Blender 5.2 animation scene.
- Normalize rendered PNGs to frame_0001.png ... frame_0128.png.
- Encode using the same FFmpeg method proven manually.
- Validate the resulting MP4 with ffprobe.
- Never return a tiny/partial MP4 as success.

INSTALL FROM PROJECT ROOT:
C:\Users\olga_Ashok3\aadwik_mvp

Stop Uvicorn, then:
Copy-Item .\AADWIK_MASTER_BATCH34\app\renderer\local_video_provider.py .\backend\app\providers\local_video_provider.py -Force
Copy-Item .\AADWIK_MASTER_BATCH34\app\renderer\aadwik_animation_scene.py .\backend\app\providers\aadwik_animation_scene.py -Force

Start backend:
cd .\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Run ONE movie. Expected:
[AADWIK ANIMATION VERIFY] PNG frames: 128/128
[AADWIK ANIMATION VERIFY] ffprobe: ...
[AADWIK ANIMATION VERIFY] SUCCESS: ...
