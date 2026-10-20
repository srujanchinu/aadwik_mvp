AADWIK MASTER BATCH 17
======================

ACTUAL LOCAL EXECUTION BOUNDARY

This batch moves from abstract render contracts toward the real local
Blender -> FFmpeg execution path.

Includes:
- Local subprocess execution boundary
- Blender EEVEE command builder
- FFmpeg frame-to-MP4 command builder
- End-to-end command orchestration
- Failure stop behavior
- 5 tests

This batch is intentionally additive. It does NOT modify your working
backend or automatically run Blender/FFmpeg.

Extract to:
C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH17

Test:
cd C:\Users\olga_Ashok3\aadwik_mvp
$env:PYTHONPATH="C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH17"
python .\AADWIK_MASTER_BATCH17\app\tests\test_master_batch17.py

Expected: 5 tests OK.

After this batch, the next integration work can connect these contracts to
the EXISTING Blender 5.2 + FFmpeg installation and current movie pipeline,
without replacing the known-working provider.
