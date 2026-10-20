from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class AlignmentFinding:
    category: str
    severity: str
    message: str

@dataclass
class AlignmentReport:
    passed: bool
    score: float
    findings: List[AlignmentFinding] = field(default_factory=list)

class AlignmentVerifier:
    """Deterministic contract for checking generated output against shot intent."""

    def verify(self, expected: Dict, actual: Dict) -> AlignmentReport:
        findings = []
        checks = [
            ("characters", "character_presence"),
            ("location", "location"),
            ("objects", "object_presence"),
            ("emotion", "emotion"),
            ("camera", "camera"),
        ]
        total = len(checks)
        passed_count = 0

        for key, category in checks:
            exp = expected.get(key)
            if exp is None:
                continue
            if actual.get(key) == exp:
                passed_count += 1
            else:
                findings.append(
                    AlignmentFinding(category, "error",
                                      f"expected={exp!r}, actual={actual.get(key)!r}")
                )

        considered = sum(1 for key, _ in checks if expected.get(key) is not None)
        score = 1.0 if considered == 0 else passed_count / considered
        return AlignmentReport(
            passed=not any(f.severity == "error" for f in findings),
            score=score,
            findings=findings,
        )
