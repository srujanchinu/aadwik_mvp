AADWIK MASTER BATCH 27
Controlled Live Backend Wiring

This batch provides an installer that makes the first real integration change to
backend/app/api/movies.py.

Behavior:
- Adds a small backend integration module under backend/app/integration/
- Adds a guarded hook to create_movie()
- Hook is DISABLED by default, so existing movie generation remains unchanged
- Installer creates a timestamped backup
- Installer refuses unexpected movies.py shapes
- Re-running is safe and does not duplicate the patch

TEST FIRST.
After the 5 tests pass, the installer may be run from the project root.
