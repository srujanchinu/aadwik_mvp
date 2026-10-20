from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ComponentRecord:
    name: str
    category: str
    status: str = "unknown"
    version: str = "1.0"
    capabilities: List[str] = field(default_factory=list)

class IntegrationRegistry:
    """Central registry for Aadwik components and provider capabilities."""

    def __init__(self):
        self._records: Dict[str, ComponentRecord] = {}

    def register(self, name: str, category: str, status: str = "ready",
                 version: str = "1.0", capabilities=None) -> ComponentRecord:
        record = ComponentRecord(
            name=name, category=category, status=status,
            version=version, capabilities=list(capabilities or [])
        )
        self._records[name] = record
        return record

    def get(self, name: str):
        return self._records.get(name)

    def all(self) -> List[ComponentRecord]:
        return list(self._records.values())

    def by_category(self, category: str) -> List[ComponentRecord]:
        return [r for r in self._records.values() if r.category == category]

    def ready(self, name: str) -> bool:
        record = self.get(name)
        return bool(record and record.status == "ready")
