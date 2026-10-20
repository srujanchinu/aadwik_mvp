from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationGate:
    ready: bool
    reasons: tuple[str, ...] = ()


def evaluate_integration_gate(
    master_pipeline_available: bool,
    backend_available: bool,
    bridge_enabled: bool,
    provider_contract_valid: bool,
) -> IntegrationGate:
    reasons = []
    if not master_pipeline_available:
        reasons.append("master_pipeline_unavailable")
    if not backend_available:
        reasons.append("backend_unavailable")
    if not bridge_enabled:
        reasons.append("bridge_disabled")
    if not provider_contract_valid:
        reasons.append("provider_contract_invalid")
    return IntegrationGate(not reasons, tuple(reasons))
