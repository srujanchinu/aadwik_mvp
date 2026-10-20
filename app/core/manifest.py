from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from typing import Any

@dataclass
class ProductionManifest:
    project_id:str
    version:str="1.0"
    created_at:str=""
    story:dict[str,Any]=None
    scenes:list=None
    shots:list=None
    def __post_init__(self):
        if not self.created_at: self.created_at=datetime.now(timezone.utc).isoformat()
        if self.story is None: self.story={}
        if self.scenes is None: self.scenes=[]
        if self.shots is None: self.shots=[]
    def to_dict(self): return asdict(self)
