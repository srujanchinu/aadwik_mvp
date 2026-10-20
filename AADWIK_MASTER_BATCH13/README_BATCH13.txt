AADWIK MASTER BATCH 13
======================

Compressed production batch:
- Explicit scene -> shot planning
- Shot contracts with camera/action/emotion/location/object requirements
- Per-shot asset requirements
- Execution contracts for provider generation
- Production batch tracking

This creates a stronger execution contract before the existing renderer is
called. It does NOT replace the working backend, Phase 23 provider, Blender,
or FFmpeg pipeline.

Extract to:
C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH13

Test:
cd C:\Users\olga_Ashok3\aadwik_mvp
$env:PYTHONPATH="C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH13"
python .\AADWIK_MASTER_BATCH13\app\tests\test_master_batch13.py

Expected: 5 tests OK.
