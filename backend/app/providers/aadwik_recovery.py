from aadwik_production_orchestrator import transition

RECOVERY_ORDER = [
    "planning", "assets", "3d_production", "audio",
    "editing", "qc", "publishing_gate"
]

def latest_checkpoint(job):
    for name in reversed(RECOVERY_ORDER):
        if name in job.checkpoints and job.checkpoints[name].get("completed"):
            return name
    return None

def recover(job):
    cp = latest_checkpoint(job)
    if cp is None:
        transition(job, "CREATED")
        return {"recovered": True, "resume_from": "planning"}
    next_state = {
        "planning": "ASSETS_READY",
        "assets": "PRODUCING",
        "3d_production": "AUDIO_READY",
        "audio": "EDITING",
        "editing": "QC",
        "qc": "READY_TO_PUBLISH",
        "publishing_gate": "READY_TO_PUBLISH",
    }[cp]
    transition(job, next_state)
    return {"recovered": True, "resume_from": cp, "state": job.state}
