from dataclasses import dataclass, field
from uuid import uuid4
from .aadwik_state import ProductionStateRecord, ProductionState, utc_now

@dataclass
class Checkpoint:
    name: str
    state: str
    payload: dict = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

@dataclass
class ProductionJob:
    job_id: str = field(default_factory=lambda:'job_'+uuid4().hex)
    project_id: str = ''
    movie_id: str|None = None
    state: ProductionStateRecord = field(default_factory=ProductionStateRecord)
    checkpoints: list = field(default_factory=list)
    def checkpoint(self,name,payload=None):
        cp=Checkpoint(name,self.state.state.value,payload or {}); self.checkpoints.append(cp); return cp
    def fail(self,message): self.state.transition(ProductionState.FAILED,error=message)
    def latest_checkpoint(self): return self.checkpoints[-1] if self.checkpoints else None
