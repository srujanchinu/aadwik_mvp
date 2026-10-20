from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class Publication:
    project_id:str
    platform:str
    media_path:str
    title:str=""
    description:str=""
    status:str="DRAFT"
    publication_id:str=field(default_factory=lambda:"pub_"+uuid4().hex)
    scheduled_at:str|None=None

class PublishingEngine:
    def __init__(self): self.publications={}
    def create(self, project_id, platform, media_path, title="", description=""):
        p=Publication(project_id,platform,media_path,title,description)
        self.publications[p.publication_id]=p
        return p
    def schedule(self,p,when):
        p.scheduled_at=when; p.status="SCHEDULED"; return p
    def approve(self,p):
        p.status="APPROVED"; return p
    def mark_published(self,p):
        if p.status!="APPROVED": raise ValueError("Publication must be approved before publishing")
        p.status="PUBLISHED"; return p
