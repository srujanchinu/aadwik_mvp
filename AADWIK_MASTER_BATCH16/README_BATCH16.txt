AADWIK MASTER BATCH 16
======================

Major media-output batch:
- FFmpeg concat assembly command generation
- Concat-list materialization
- FFprobe-style media metadata validation contract
- Verified RenderArtifact
- Final assembly gate requiring verified artifacts

This is additive. It does NOT overwrite the working backend, Blender provider,
FFmpeg installation, or previous batches.

Extract to:
C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH16

Test:
cd C:\Users\olga_Ashok3\aadwik_mvp
$env:PYTHONPATH="C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH16"
python .\AADWIK_MASTER_BATCH16\app\tests\test_master_batch16.py

Expected: 5 tests OK.

Note:
The batch creates the execution contract; it does not automatically modify
or execute your existing production backend.
