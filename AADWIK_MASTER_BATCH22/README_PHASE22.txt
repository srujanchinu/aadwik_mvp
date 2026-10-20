AADWIK MASTER BATCH 22
Real Backend Pipeline Integration & Production Job Wiring

Purpose:
Create the concrete adapter contract needed to connect Aadwik's master production
pipeline to the existing FastAPI movie-generation backend without overwriting it.

This batch remains self-contained. It does not edit backend/app, start Uvicorn,
call Blender/FFmpeg, or require provider credentials.

Design:
- backend job lifecycle mapping
- request normalization
- pipeline event -> backend progress mapping
- safe status synchronization
- explicit integration boundary
- failure normalization

Use this batch as the integration layer before making changes to the live backend.
