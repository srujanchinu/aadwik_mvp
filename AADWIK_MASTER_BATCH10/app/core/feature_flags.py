from typing import Dict

class FeatureFlags:
    """Small deterministic feature-flag layer for staged Aadwik rollout."""

    def __init__(self, initial=None):
        self._flags: Dict[str, bool] = dict(initial or {})

    def set(self, name: str, enabled: bool) -> None:
        self._flags[name] = bool(enabled)

    def enabled(self, name: str, default: bool = False) -> bool:
        return self._flags.get(name, default)

    def snapshot(self) -> Dict[str, bool]:
        return dict(self._flags)
