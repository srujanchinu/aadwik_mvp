from dataclasses import dataclass


MARKER = "# AADWIK_MASTER_BATCH26_LIVE_INTEGRATION"


@dataclass(frozen=True)
class LiveIntegrationContract:
    target: str = "backend/app/api/movies.py"
    marker: str = MARKER
    backup_before_write: bool = True
    preserve_existing_generation: bool = True


def target_is_compatible(text: str) -> bool:
    required = ("APIRouter", "router", "/movies")
    return all(item in text for item in required)


def integration_block() -> str:
    return (
        "\n"
        f"{MARKER}\n"
        "# Controlled master-pipeline handoff point.\n"
        "# Existing movie-generation behavior is preserved.\n"
    )
