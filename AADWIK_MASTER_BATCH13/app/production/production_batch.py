from dataclasses import dataclass, field
from typing import List

@dataclass
class ProductionBatch:
    project_id: str
    contracts: List = field(default_factory=list)

    def add(self, contract):
        self.contracts.append(contract)

    def pending(self):
        return [c for c in self.contracts if c.status == "planned"]

    def failed(self):
        return [c for c in self.contracts if c.status == "failed"]

    def generated(self):
        return [c for c in self.contracts if c.status == "generated"]

    def complete(self):
        return bool(self.contracts) and all(
            c.status == "generated" for c in self.contracts
        )
