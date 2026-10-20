from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class AssetLock:
    asset_id: str
    asset_type: str
    identity: Dict = field(default_factory=dict)
    locked: bool = True
    version: int = 1

class AssetLockManager:
    def __init__(self):
        self._locks = {}

    def lock(self, asset_id, asset_type, identity=None):
        current = self._locks.get(asset_id)
        if current:
            current.identity.update(dict(identity or {}))
            current.version += 1
            current.locked = True
            return current
        item = AssetLock(asset_id, asset_type, dict(identity or {}))
        self._locks[asset_id] = item
        return item

    def get(self, asset_id):
        return self._locks.get(asset_id)

    def validate(self, asset_id, observed: Dict) -> List[str]:
        item = self.get(asset_id)
        if not item or not item.locked:
            return [f"unlocked_asset:{asset_id}"]
        return [f"identity_mismatch:{k}" for k, v in item.identity.items()
                if observed.get(k) != v]
