MARKER = "# AADWIK_BATCH27_LIVE_HOOK"


def compatible_movies_file(text: str) -> bool:
    return (
        "def create_movie(" in text
        and "background_tasks.add_task(" in text
        and "run_movie_generation" in text
        and "created_movie = store.create(" in text
    )


def already_patched(text: str) -> bool:
    return MARKER in text


def import_line() -> str:
    return (
        "from app.integration.live_runtime import "
        "dispatch_master_runtime\n"
    )


def hook_block() -> str:
    return (
        "\n    " + MARKER + "\n"
        "    # Guarded master-pipeline handoff; disabled by default.\n"
        "    dispatch_master_runtime(movie_id, created_movie)\n"
    )


def patch_text(text: str) -> str:
    if not compatible_movies_file(text):
        raise ValueError("unexpected movies.py shape")
    if already_patched(text):
        return text

    lines = text.splitlines()
    # Add import after the existing LocalVideoProvider import when possible.
    import_index = None
    for i, line in enumerate(lines):
        if "from app.providers.local_video_provider import LocalVideoProvider" in line:
            import_index = i + 1
            break
    if import_index is None:
        raise ValueError("LocalVideoProvider import not found")

    lines.insert(import_index, import_line().rstrip("\n"))
    patched = "\n".join(lines)

    anchor = """    created_movie = store.create(
        movie
    )
"""
    if anchor not in patched:
        raise ValueError("store.create anchor not found")

    patched = patched.replace(
        anchor,
        anchor + hook_block() + "\n",
        1,
    )
    return patched + ("\n" if text.endswith("\n") else "")
