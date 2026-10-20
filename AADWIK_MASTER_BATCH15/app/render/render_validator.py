from dataclasses import dataclass, field
from typing import List

@dataclass
class RenderValidation:
    passed: bool
    issues: List[str] = field(default_factory=list)

class RenderValidator:
    def validate_job(self, job) -> RenderValidation:
        issues = []
        if job.width <= 0 or job.height <= 0:
            issues.append("invalid_resolution")
        if job.fps <= 0:
            issues.append("invalid_fps")
        if job.frames <= 0:
            issues.append("invalid_frame_count")
        if job.status == "rendered" and not job.output_path:
            issues.append("missing_output_path")
        return RenderValidation(not issues, issues)

    def validate_provider_result(self, result) -> RenderValidation:
        issues = []
        if not result.success:
            issues.append(result.error or "provider_failed")
        if result.success and not result.output_path:
            issues.append("provider_returned_no_output")
        return RenderValidation(not issues, issues)
