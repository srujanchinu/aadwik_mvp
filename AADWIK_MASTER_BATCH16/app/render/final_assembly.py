from dataclasses import dataclass, field
from typing import List

@dataclass
class FinalAssembly:
    project_id: str
    artifacts: List = field(default_factory=list)
    output_path: str = ""
    status: str = "planned"

    def add_verified(self, artifact):
        if not artifact.verified:
            raise ValueError("artifact_not_verified")
        self.artifacts.append(artifact)

    def validate(self):
        if not self.artifacts:
            return False, ["no_verified_artifacts"]
        return True, []

    def mark_ready(self, output_path):
        ok, issues = self.validate()
        if not ok:
            raise ValueError(";".join(issues))
        self.output_path = output_path
        self.status = "ready"
