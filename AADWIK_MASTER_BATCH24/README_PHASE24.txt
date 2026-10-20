AADWIK MASTER BATCH 24
Live Backend Wiring — Safe Movie Generation Integration

Purpose:
Provide the final, controlled wiring layer for the existing FastAPI movie-generation
flow. The installer is intentionally opt-in and creates a backup before changing any
backend file.

IMPORTANT:
1. Extract this batch.
2. Run the tests first.
3. Do NOT run the installer until instructed after tests pass.
4. The installer targets backend/app/api/movies.py only.
5. It creates a timestamped backup before modifying the target.
6. Existing provider files and Phase 23 cinematic files are not overwritten.

The integration hook is designed to preserve the existing movie endpoint while adding
a master-pipeline integration boundary. If the expected marker/function shape is not
found, the installer refuses to modify the file.
