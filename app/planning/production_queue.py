from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

def now(): return datetime.now(timezone.utc).isoformat()

@dataclass
class QueueItem:
    item_id:str=field(default_factory=lambda:"queue_"+uuid4().hex)
    project_id:str=""
    priority:int=50
    status:str="QUEUED"
    created_at:str=field(default_factory=now)

class ProductionQueue:
    def __init__(self): self.items=[]
    def add(self,item): self.items.append(item); return item
    def next_item(self):
        pending=[x for x in self.items if x.status=="QUEUED"]
        return sorted(pending,key=lambda x:(-x.priority,x.created_at))[0] if pending else None
    def mark_running(self,item): item.status="RUNNING"; return item
    def mark_complete(self,item): item.status="COMPLETE"; return item
