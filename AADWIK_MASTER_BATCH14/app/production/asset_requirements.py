from dataclasses import dataclass
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
        out = [AssetRequirement(f"character:{n}", "character") for n in shot.characters]
        if shot.location:
            out.append(AssetRequirement(f"location:{shot.location}", "location"))
        out.extend(AssetRequirement(f"object:{n}", "object") for n in shot.objects)
        return out
