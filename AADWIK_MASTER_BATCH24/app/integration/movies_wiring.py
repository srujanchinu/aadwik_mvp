from dataclasses import dataclass


@dataclass(frozen=True)
class MoviesWiringPlan:
    target: str
    backup_required: bool = True
    require_marker: bool = True
    preserve_provider: bool = True
    preserve_phase23: bool = True


DEFAULT_PLAN = MoviesWiringPlan(
    target="backend/app/api/movies.py"
)


def validate_target_text(text: str) -> bool:
    """Refuse blind modification unless the expected movies router is present."""
    required = ("APIRouter", "router", "/movies")
    return all(token in text for token in required)
