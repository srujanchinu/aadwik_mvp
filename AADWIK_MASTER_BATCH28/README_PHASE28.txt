AADWIK MASTER BATCH 28
Phase 23 Character Provider Dependency Repair

Purpose:
Repair the live backend dependency that caused Blender to fail at 0%:
ModuleNotFoundError: No module named 'aadwik_character_quality'

This batch copies the Phase 23 character-quality module into the live backend
providers directory and verifies that it is importable.

IMPORTANT:
- Stop the backend/Uvicorn before applying the live copy.
- Do not modify movies.py.
- Do not modify Blender or FFmpeg.
- A backup of any existing backend copy is created.
- Test this batch before running the installer.
