from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Idea:
    title:str
    premise:str
    tags:list=field(default_factory=list)
    idea_id:str=field(default_factory=lambda:"idea_"+uuid4().hex)
    status:str="IDEA"

class IdeaBank:
    def __init__(self): self.items=[]
    def add(self,idea): self.items.append(idea); return idea
    def search(self,term):
        q=term.lower()
        return [x for x in self.items if q in x.title.lower() or q in x.premise.lower() or any(q in t.lower() for t in x.tags)]
    def promote(self,idea): idea.status="PLANNED"; return idea
