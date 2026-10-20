from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class StageContract:
    name: str
    required_inputs: tuple[str, ...]
    produced_outputs: tuple[str, ...]


DEFAULT_CONTRACTS = (
    StageContract("story_understanding", ("story",), ("story_context",)),
    StageContract("scene_breakdown", ("story_context",), ("scenes",)),
    StageContract("character_world_lock", ("scenes",), ("identity_lock",)),
    StageContract("shot_planning", ("scenes", "identity_lock"), ("shots",)),
    StageContract("generation", ("shots",), ("renders",)),
    StageContract("alignment_verification", ("renders", "shots"), ("verification",)),
    StageContract("repair", ("verification",), ("repaired_renders",)),
    StageContract("final_assembly", ("repaired_renders",), ("master_artifact",)),
    StageContract("quality_gate", ("master_artifact",), ("quality_result",)),
    StageContract("publish_readiness", ("quality_result",), ("publish_ready",)),
)


def validate_contract_chain(contracts=DEFAULT_CONTRACTS) -> Dict[str, Any]:
    """Ensure every non-first stage consumes an output produced upstream."""
    available = {"story"}
    errors = []

    for contract in contracts:
        missing = [x for x in contract.required_inputs if x not in available]
        if missing:
            errors.append({
                "stage": contract.name,
                "missing_inputs": missing,
            })
        available.update(contract.produced_outputs)

    return {"valid": not errors, "errors": errors, "available_outputs": sorted(available)}
