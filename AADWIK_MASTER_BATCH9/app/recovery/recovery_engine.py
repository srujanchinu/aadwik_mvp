from dataclasses import dataclass, field
from datetime import datetime, timezone

def now(): return datetime.now(timezone.utc).isoformat()

@dataclass
class RecoveryCheckpoint:
    name:str
    payload:dict=field(default_factory=dict)
    created_at:str=field(default_factory=now)

@dataclass
class RecoveryManager:
    checkpoints:list=field(default_factory=list)
    failures:list=field(default_factory=list)

    def save(self,name,payload=None):
        cp=RecoveryCheckpoint(name,payload or {})
        self.checkpoints.append(cp)
        return cp

    def record_failure(self,stage,error):
        item={"stage":stage,"error":str(error),"created_at":now()}
        self.failures.append(item)
        return item

    def latest(self):
        return self.checkpoints[-1] if self.checkpoints else None

    def can_resume(self):
        return bool(self.checkpoints)
