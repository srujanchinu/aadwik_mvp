from aadwik_production_orchestrator import create_job, transition, checkpoint

job = create_job("the_last_star", "movie", [{"scene": i} for i in range(14)])
transition(job, "PLANNED")
checkpoint(job, "planning")
assert job.project_id == "the_last_star"
assert job.state == "PLANNED"
assert "planning" in job.checkpoints
print("PROJECT -> PRODUCTION JOB: CONNECTED")
print("MOVIE JOB CREATED: OK")
print("CHECKPOINT SYSTEM: OK")
print("STEP 13A PASS")
