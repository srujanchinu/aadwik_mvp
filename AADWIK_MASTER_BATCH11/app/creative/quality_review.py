from dataclasses import dataclass, field
from typing import List

@dataclass
class ReviewFinding:
    category: str
    severity: str
    message: str

@dataclass
class QualityReview:
    passed: bool
    findings: List[ReviewFinding] = field(default_factory=list)

class CreativeQualityReviewer:
    """Quality gate for story/scene intent before expensive generation."""

    def review(self, scene_intent, canon_issues=None, continuity_issues=None):
        findings = []
        for issue in canon_issues or []:
            findings.append(ReviewFinding("canon", "error", issue))
        for issue in continuity_issues or []:
            findings.append(ReviewFinding("continuity", "error", issue))

        if not scene_intent.purpose:
            findings.append(ReviewFinding("story", "error", "missing_purpose"))

        return QualityReview(
            passed=not any(f.severity == "error" for f in findings),
            findings=findings,
        )
