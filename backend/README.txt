
AADWIK COMPLETE 3D PIPELINE

Files:
backend/app/providers/story_visual_planner.py
backend/app/providers/visual_router.py
backend/app/providers/local_video_provider.py
backend/app/providers/aadwik_blender_scene.py

This package is compatible with the existing movies.py call:
provider.generate_video(prompt=..., output_path=..., aspect_ratio=...)

It preserves analyze_story() compatibility.

IMPORTANT:
- Local Blender is still a free procedural 3D development renderer.
- It now consumes a structured scene plan and creates separate environments,
  props, characters and camera/action changes per story scene.
- It is NOT claimed to be final anime-quality character generation.
- Blender 5.2 uses BLENDER_EEVEE.

Replace these FOUR provider files together.

Then:
cd C:\Users\olga_Ashok3\aadwik_mvp\backend
python -c "from app.providers.story_visual_planner import analyze_story; p=analyze_story('On the night of a village festival, a girl named Tara sees a blue star fall into a forest. She follows it and meets an injured guardian. Together they cross a glowing river and enter an ancient temple where they face a shadow creature. At sunrise Tara returns home.'); print(p['production_summary']); print([(s['scene_number'],s['type'],s['location']['name']) for s in p['scenes']])"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

For the first movie test use 1 minute in the UI, but the local renderer intentionally renders a short validation sequence.
