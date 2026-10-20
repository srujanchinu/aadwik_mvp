AADWIK MASTER BATCH 14 — FIXED
==============================

This corrected package is fully self-contained. It no longer depends on
Batch 13 and therefore avoids the Python "app" package collision.

Extract to:
C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH14

Test:
cd C:\Users\olga_Ashok3\aadwik_mvp
$env:PYTHONPATH="C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH14"
python .\AADWIK_MASTER_BATCH14\app\tests\test_master_batch14.py

Expected: 5 tests OK.
