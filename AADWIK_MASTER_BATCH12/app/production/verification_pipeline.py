from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class VerificationOutcome:
    status: str
    alignment_score: float
    repair_required: bool
    reason: str = ""

class VerificationPipeline:
    """Generation -> alignment verification -> targeted repair decision."""

    def __init__(self, verifier, repair_planner):
        self.verifier = verifier
        self.repair_planner = repair_planner

    def evaluate(self, expected: Dict, actual: Dict,
                 minimum_score: float = 1.0) -> VerificationOutcome:
        report = self.verifier.verify(expected, actual)
        plan = self.repair_planner.plan(report)

        if report.score >= minimum_score and report.passed:
            return VerificationOutcome(
                "approved", report.score, False, "alignment_passed"
            )

        reason = "alignment_failed"
        if plan.required:
            reason = "targeted_repair_required"
        return VerificationOutcome(
            "repair_required", report.score, plan.required, reason
        )
