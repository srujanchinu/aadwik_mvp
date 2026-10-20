AADWIK MASTER BATCH 23
Production Backend Integration Adapter

Purpose:
Bridge the master pipeline contracts to an existing movie-generation backend
through a narrow, injectable adapter. No existing backend files are overwritten.
No external provider calls are made by this batch.

The adapter accepts a backend callable so the real FastAPI movie-generation
function can be connected later without changing the master pipeline contracts.

Safety:
- isolated package
- dependency injection
- dry-run support
- deterministic progress mapping
- normalized success/failure results
