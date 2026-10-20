from aadwik_production_orchestrator import transition, checkpoint, build_production_package

REQUIRED = [
    "story", "shot_plan", "assets", "worlds", "acting",
    "camera", "audio", "edit", "qc"
]

def validate_movie_input(payload):
    missing = [k for k in REQUIRED if not payload.get(k)]
    return {"valid": not missing, "missing": missing}

def run_movie_pipeline(job, payload):
    check = validate_movie_input(payload)
    if not check["valid"]:
        raise ValueError("Missing production inputs: " + ", ".join(check["missing"]))

    transition(job, "PLANNED"); checkpoint(job, "planning")
    transition(job, "ASSETS_READY"); checkpoint(job, "assets")
    transition(job, "PRODUCING"); checkpoint(job, "3d_production")
    transition(job, "AUDIO_READY"); checkpoint(job, "audio")
    transition(job, "EDITING"); checkpoint(job, "editing")
    transition(job, "QC"); checkpoint(job, "qc", payload.get("qc"))
    transition(job, "READY_TO_PUBLISH"); checkpoint(job, "publishing_gate")
    return build_production_package(job)
