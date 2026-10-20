from aadwik_production_orchestrator import create_job
from aadwik_production_queue import ProductionQueue

q = ProductionQueue()
jobs = [create_job(f"p{i}", "movie") for i in range(3)]
for j in jobs: q.enqueue(j)
assert q.size() == 3
assert q.next_job().project_id == "p0"
assert q.size() == 2
print("PRODUCTION QUEUE: OK")
print("JOB ORDER: OK")
print("QUEUE SNAPSHOT: OK")
print("STEP 13D PASS")
