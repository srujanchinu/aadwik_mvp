AADWIK MASTER BATCH 15
======================

Major production execution batch:
- RenderJob lifecycle
- Provider adapter contract
- Render validation
- Render queue
- Success/failure normalization
- Shot duration derived from frame count / FPS

This is additive. It does NOT overwrite the existing working backend,
Phase 23 provider, Blender, or FFmpeg setup.

Extract to:
C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH15

Test:
cd C:\Users\olga_Ashok3\aadwik_mvp
$env:PYTHONPATH="C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH15"
python .\AADWIK_MASTER_BATCH15\app\tests\test_master_batch15.py

Expected: 5 tests OK.

Important:
This batch defines the execution contract first. Actual wiring into the
existing FastAPI movie pipeline will be done in a later integration batch,
after the contracts are proven independently.
