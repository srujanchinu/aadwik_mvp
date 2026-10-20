from dataclasses import dataclass
from typing import List


@dataclass
class ResumePoint:
    job_id: str
    last_passed_stage: str | None
    next_stage: str | None
    resumable: bool


def calculate_resume_point(job_id: str, stage_order: List[str], passed_stages: List[str]) -> ResumePoint:
    if not job_id:
        raise ValueError("job_id is required")
    if not stage_order:
        return ResumePoint(job_id, None, None, False)

    passed = [s for s in stage_order if s in set(passed_stages)]
    last = passed[-1] if passed else None

    if len(passed) == len(stage_order):
        return ResumePoint(job_id, last, None, False)

    next_stage = stage_order[len(passed)]
    return ResumePoint(job_id, last, next_stage, True)
