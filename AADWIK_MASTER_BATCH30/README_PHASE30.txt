AADWIK MASTER BATCH 30
======================
Phase 23 Character API Restore

Problem fixed:
The live aadwik_blender_scene.py imports the Phase 23 Blender-native builders
build_tara, build_guardian, build_shadow, build_blue_star and apply_emotion.
Batch 29 installed a dependency-free compatibility module that did not expose
those Blender-native builder functions. This batch restores the exact Phase 23
character-quality implementation packaged in AADWIK_PHASE23_CHARACTER_CINEMATIC_UPGRADE.

Installer:
Run from project root:
python .\AADWIK_MASTER_BATCH30\tools\install_batch30.py

Then restart backend and run the same one-line 3D smoke test.
Do not modify Blender or FFmpeg.
