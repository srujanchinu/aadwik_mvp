class IntegrationFeatureGate:
    """Explicit opt-in gate; defaults to safe disabled mode."""

    def __init__(self, enabled: bool = False):
        self._enabled = bool(enabled)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False
