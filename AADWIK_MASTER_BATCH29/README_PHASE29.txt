AADWIK MASTER BATCH 29
Self-Contained Phase 23 Character Dependency Recovery

Fixes the live Blender import failure:
ModuleNotFoundError: No module named 'aadwik_character_quality'

This package includes the required dependency directly, so it does not depend on
an old Phase 23 extraction being present.

The installer:
- targets backend/app/providers/aadwik_character_quality.py
- backs up an existing live copy
- validates required symbols
- does not modify movies.py
- does not modify Blender or FFmpeg

TEST FIRST, then install.
