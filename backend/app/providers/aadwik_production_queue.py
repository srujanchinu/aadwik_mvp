from collections import deque

class ProductionQueue:
    def __init__(self):
        self._queue = deque()
        self._jobs = {}

    def enqueue(self, job):
        self._queue.append(job.job_id)
        self._jobs[job.job_id] = job
        return job.job_id

    def next_job(self):
        if not self._queue:
            return None
        return self._jobs[self._queue.popleft()]

    def size(self):
        return len(self._queue)

    def snapshot(self):
        return [{"job_id": j, "state": self._jobs[j].state} for j in self._jobs]
