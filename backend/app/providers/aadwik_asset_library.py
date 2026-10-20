import json
from pathlib import Path

ASSET_LIBRARY_VERSION = "1.0"

ASSET_LIBRARY = {
    "char_tara_v1": {
        "asset_id": "char_tara_v1",
        "type": "character",
        "name": "Tara",
        "builder_root": "CHAR_TARA_ROOT",
        "locked": True,
        "reuse_policy": "exact",
        "design_lock": {
            "age": 12,
            "hair": "dark shoulder-length hair",
            "skin": "warm brown",
            "clothing": "blue dress with gold sash",
            "identity_rule": "do not redesign between shots"
        }
    },
    "char_guardian_v1": {
        "asset_id": "char_guardian_v1",
        "type": "character",
        "name": "Guardian",
        "builder_root": "CHAR_GUARDIAN_ROOT",
        "locked": True,
        "reuse_policy": "exact",
        "design_lock": {
            "body": "small blue magical creature",
            "eyes": "large expressive eyes",
            "state": "injured guardian",
            "identity_rule": "do not redesign between shots"
        }
    },
    "char_shadow_creature_v1": {
        "asset_id": "char_shadow_creature_v1",
        "type": "character",
        "name": "Shadow Creature",
        "builder_root": "CHAR_SHADOW_ROOT",
        "locked": True,
        "reuse_policy": "exact",
        "design_lock": {
            "silhouette": "tall dark supernatural figure",
            "eyes": "bright expressive eyes",
            "identity_rule": "do not redesign between shots"
        }
    },
    "prop_blue_star_v1": {
        "asset_id": "prop_blue_star_v1",
        "type": "prop",
        "name": "Blue Star",
        "builder_root": "PROP_BLUE_STAR",
        "locked": True,
        "reuse_policy": "exact",
        "design_lock": {
            "appearance": "small luminous blue magical star",
            "identity_rule": "same hero prop throughout story"
        }
    }
}

def get_asset(asset_id):
    return ASSET_LIBRARY.get(asset_id)

def validate_asset_id(asset_id):
    asset = get_asset(asset_id)
    if not asset:
        raise ValueError(f"Unknown Aadwik asset: {asset_id}")
    if not asset["locked"]:
        raise ValueError(f"Asset is not locked: {asset_id}")
    return asset

def resolve_scene_assets(asset_ids):
    resolved = []
    seen = set()
    for asset_id in asset_ids:
        if asset_id in seen:
            continue
        resolved.append(validate_asset_id(asset_id))
        seen.add(asset_id)
    return resolved

def save_manifest(output_path):
    payload = {
        "schema": "aadwik-asset-library-1.0",
        "version": ASSET_LIBRARY_VERSION,
        "asset_count": len(ASSET_LIBRARY),
        "assets": list(ASSET_LIBRARY.values())
    }
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
