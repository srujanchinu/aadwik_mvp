
AADWIK PHASE 23 FINAL ROUTE LOCK

This package fixes the remaining integration risk: a generated movie must
never be assembled from stale backend\ffmpeg_sequence or backend\frames.

Replace:
backend\app\providers\local_video_provider.py

The provider now creates:
backend\generated\<movie_id>_phase23\
    phase23_production_plan.json
    rendered_frames\
        frame_000001.png
        ...
    and writes:
backend\generated\<movie_id>.mp4

It validates that the MP4 was encoded from THIS generation's rendered_frames.

Run:
python tests\test_phase23_final_route.py
python -m py_compile app\providers\local_video_provider.py

Then restart Uvicorn and generate one movie.

The terminal should show:
[AADWIK FINAL ROUTE] Work directory: ...\<movie_id>_phase23
[AADWIK FINAL ROUTE] Encoding ONLY: ...\rendered_frames
[AADWIK FINAL ROUTE] MP4 VALIDATED: ...\<movie_id>.mp4
