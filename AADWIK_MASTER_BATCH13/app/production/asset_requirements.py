from dataclasses import dataclass, field
from typing import List

@dataclass
class AssetRequirement:
    asset_id: str
    asset_type: str
    source: str = "library_or_provider"
    required: bool = True
    locked: bool = True
    notes: str = ""

class AssetRequirementBuilder:
    def build_for_shot(self, shot) -> List[AssetRequirement]:
        assets = []
        for name in shot.characters:
            assets.append(AssetRequirement(f"character:{name}", "character"))
        if shot.location:
            assets.append(AssetRequirement(f"location:{shot.location}", "location"))
        for name in shot.objects:
            assets.append(AssetRequirement(f"object:{name}", "object"))
        return assets
