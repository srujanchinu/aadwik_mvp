TERMINAL = {"completed", "failed", "cancelled"}


def validate_transition(previous, current):
    if previous in TERMINAL and current != previous:
        raise ValueError("terminal status cannot regress")
    return True


def normalize_runtime_status(status, progress):
    if status not in {"queued", "running", "verifying", "repairing",
                      "assembling", "completed", "failed", "cancelled"}:
        raise ValueError("invalid runtime status")
    if not 0 <= progress <= 100:
        raise ValueError("progress must be between 0 and 100")
    return {"status": status, "progress": progress}
