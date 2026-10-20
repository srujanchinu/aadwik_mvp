from dataclasses import dataclass, field
from typing import List

@dataclass
class RenderQueue:
    jobs: List = field(default_factory=list)

    def enqueue(self, job):
        self.jobs.append(job)

    def next(self):
        for job in self.jobs:
            if job.status == "queued":
                return job
        return None

    def pending(self):
        return [j for j in self.jobs if j.status == "queued"]

    def completed(self):
        return [j for j in self.jobs if j.status == "rendered"]

    def failed(self):
        return [j for j in self.jobs if j.status == "failed"]
