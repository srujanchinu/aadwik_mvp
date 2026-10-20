AADWIK MASTER BATCH 26
Actual Backend Integration — Safe Installer

This batch introduces the real, controlled integration installer for the existing
backend/app/api/movies.py.

It does NOT blindly replace movies.py. Before changing anything it:
- verifies the expected FastAPI movie router shape
- creates a timestamped backup
- checks for the Batch 26 marker
- installs only a small integration marker/configuration block
- refuses to proceed when the target shape is unexpected

The live movie-generation implementation remains intact. The marker is the
controlled handoff point for the master runtime bridge.

TEST FIRST. Do not run the installer until the 5 tests pass.
