from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class ScheduleItem:
    publication_id:str
    run_at:str
    status:str="SCHEDULED"
    schedule_id:str=field(default_factory=lambda:"sched_"+uuid4().hex)

def validate_iso_datetime(value):
    datetime.fromisoformat(value.replace("Z","+00:00"))
    return True

class Scheduler:
    def __init__(self): self.items=[]
    def add(self,publication_id,run_at):
        validate_iso_datetime(run_at)
        item=ScheduleItem(publication_id,run_at); self.items.append(item); return item
    def cancel(self,item):
        item.status="CANCELLED"; return item
