class ProductionIntegrationSwitch:
    """Explicit runtime switch; defaults off so existing backend behavior is protected."""

    def __init__(self, enabled: bool = False):
        self.enabled = bool(enabled)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def require_enabled(self):
        if not self.enabled:
            raise RuntimeError("production integration switch is disabled")
