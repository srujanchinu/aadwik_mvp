MARKER = "# AADWIK_MASTER_LIVE_WIRING_V24"


def has_marker(text: str) -> bool:
    return MARKER in text


def marker_block() -> str:
    return (
        "\n"
        f"{MARKER}\n"
        "# Master integration hook is intentionally inert until explicitly enabled.\n"
        "# Existing movie-generation behavior remains the source of truth.\n"
    )
