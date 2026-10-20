AADWIK MASTER BATCH 2 — FIXED PACKAGE

Extract this folder to:
C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH2\

Test from:
C:\Users\olga_Ashok3\aadwik_mvp

PowerShell:
$env:PYTHONPATH="C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH2"
python -m unittest discover -s AADWIK_MASTER_BATCH2\app\tests -p "test_*.py" -v

This is a standalone additive batch for testing. Do not overwrite backend/app until tests pass.
