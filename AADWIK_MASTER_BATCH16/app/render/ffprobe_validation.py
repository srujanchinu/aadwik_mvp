from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class MediaValidation:
    passed: bool
    issues: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

class MediaValidator:
    """Validates normalized media metadata before final assembly."""

    def validate(self, metadata: Dict, expected: Dict) -> MediaValidation:
        issues = []
        for key, value in expected.items():
            if metadata.get(key) != value:
                issues.append(f"metadata_mismatch:{key}")

        duration = metadata.get("duration")
        if duration is not None and duration <= 0:
            issues.append("invalid_duration")

        return MediaValidation(not issues, issues, dict(metadata))
