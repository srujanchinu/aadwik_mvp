from dataclasses import dataclass, field
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).isoformat()

@dataclass
class PipelineContext:
    project_id: str
    story: dict = field(default_factory=dict)
    scenes: list = field(default_factory=list)
    shots: list = field(default_factory=list)
    checkpoints: list = field(default_factory=list)
    status: str = "DRAFT"

    def checkpoint(self, name):
        item={"name":name,"status":self.status,"created_at":now()}
        self.checkpoints.append(item)
        return item

def build_pipeline(project_id, story, scenes, shots):
    ctx=PipelineContext(project_id, story, scenes, shots)
    ctx.status="PLANNED"
    ctx.checkpoint("pipeline_planned")
    return ctx
