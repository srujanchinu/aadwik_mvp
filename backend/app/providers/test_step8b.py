from pathlib import Path
from aadwik_asset_library import ASSET_LIBRARY, resolve_scene_assets, save_manifest

assert len(ASSET_LIBRARY) == 4

scene_assets = resolve_scene_assets([
    "char_tara_v1",
    "char_tara_v1",
    "char_guardian_v1",
    "prop_blue_star_v1",
])

assert [a["asset_id"] for a in scene_assets] == [
    "char_tara_v1",
    "char_guardian_v1",
    "prop_blue_star_v1",
]
assert all(a["locked"] for a in scene_assets)

out = Path("step8b_asset_manifest.json")
save_manifest(out)
assert out.exists()

print("ASSET LIBRARY VERSION:", "1.0")
print("TOTAL LOCKED ASSETS:", len(ASSET_LIBRARY))
print("SCENE RESOLUTION:", [a["asset_id"] for a in scene_assets])
print("DUPLICATE REUSE: OK")
print("LOCKED IDENTITY: OK")
print("MANIFEST:", out.resolve())
print("STEP 8B PASS")
