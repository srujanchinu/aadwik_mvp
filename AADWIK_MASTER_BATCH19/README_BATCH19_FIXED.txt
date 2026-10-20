AADWIK MASTER BATCH 19 — FIXED

The previous package omitted progress_events.py. This corrected package is
fully self-contained.

Extract to:
C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH19

Test:
cd C:\Users\olga_Ashok3\aadwik_mvp
$env:PYTHONPATH="C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH19"
python .\AADWIK_MASTER_BATCH19\app\tests\test_master_batch19.py

Expected: 5 tests OK.
