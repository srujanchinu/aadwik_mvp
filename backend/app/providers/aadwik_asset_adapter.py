import json
from pathlib import Path

ASSET_ROOTS = {
    "char_tara_v1": "CHAR_TARA_ROOT",
    "char_guardian_v1": "CHAR_GUARDIAN_ROOT",
    "char_shadow_creature_v1": "CHAR_SHADOW_ROOT",
    "prop_blue_star_v1": "PROP_BLUE_STAR",
}

def attach_locked_assets(blender_job):
    """Resolve production-job asset IDs to locked Blender asset roots."""
    job = dict(blender_job)
    shots = job.get("shots", [])
    resolved = 0

    for shot in shots:
        asset_ids = shot.get("asset_ids", [])
        roots = []
        for asset_id in asset_ids:
            if asset_id not in ASSET_ROOTS:
                raise ValueError(f"Unknown locked asset: {asset_id}")
            roots.append(ASSET_ROOTS[asset_id])
        shot["locked_asset_roots"] = roots
        shot["asset_reuse_locked"] = True
        resolved += len(roots)

    job["asset_library"] = {
        "schema": "aadwik-asset-library-1.0",
        "reuse_mode": "exact",
        "identity_locked": True,
        "resolved_asset_references": resolved,
    }
    return job

def save_job(job, path):
    Path(path).write_text(json.dumps(job, indent=2), encoding="utf-8")
