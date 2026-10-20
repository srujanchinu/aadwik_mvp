from aadwik_production_orchestrator import create_job, transition, checkpoint, fail
from aadwik_recovery import recover

job = create_job("recover_test")
transition(job, "ASSETS_READY")
checkpoint(job, "assets")
fail(job, "temporary render interruption", recoverable=True)
result = recover(job)
assert result["recovered"] and result["resume_from"] == "assets"
assert job.state == "PRODUCING"
print("FAILURE DETECTION: OK")
print("CHECKPOINT RECOVERY: OK")
print("RESUME FROM LAST SAFE POINT: OK")
print("STEP 13E PASS")
