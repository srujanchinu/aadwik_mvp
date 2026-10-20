AADWIK MASTER BATCH 18
======================

REAL INTEGRATION BRIDGE

This batch connects the previously defined production contracts at the
application boundary without overwriting the working backend.

Includes:
- RenderBridge
- MovieGenerationAdapter
- Progress event stream for UI/API updates
- Integration readiness status
- Renderer success/failure propagation
- 5 tests

Extract to:
C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH18

Test:
cd C:\Users\olga_Ashok3\aadwik_mvp
$env:PYTHONPATH="C:\Users\olga_Ashok3\aadwik_mvp\AADWIK_MASTER_BATCH18"
python .\AADWIK_MASTER_BATCH18\app\tests\test_master_batch18.py

Expected: 5 tests OK.

IMPORTANT:
This is the safe integration boundary. It intentionally does not edit
backend/app/api/movies.py yet. The next integration batch can wire the
bridge into the existing run_movie_generation flow after these contracts
are verified.
