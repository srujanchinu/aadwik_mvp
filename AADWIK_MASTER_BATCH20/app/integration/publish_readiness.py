from dataclasses import dataclass


@dataclass(frozen=True)
class PublishReadiness:
    ready: bool
    reasons: tuple[str, ...] = ()


def evaluate_publish_readiness(
    production_complete: bool,
    quality_passed: bool,
    approved: bool,
    artifact_present: bool,
) -> PublishReadiness:
    reasons = []
    if not production_complete:
        reasons.append("production_incomplete")
    if not quality_passed:
        reasons.append("quality_gate_failed")
    if not approved:
        reasons.append("approval_required")
    if not artifact_present:
        reasons.append("final_artifact_missing")

    return PublishReadiness(not reasons, tuple(reasons))
