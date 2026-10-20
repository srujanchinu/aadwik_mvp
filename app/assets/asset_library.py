from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Asset:
    name:str
    kind:str
    path:str=""
    asset_id:str=field(default_factory=lambda:"asset_"+uuid4().hex)
    version:int=1
    metadata:dict=field(default_factory=dict)

class AssetLibrary:
    def __init__(self): self.assets={}
    def add(self,asset): self.assets[asset.asset_id]=asset; return asset
    def get(self,asset_id): return self.assets.get(asset_id)
    def versions(self,name):
        return [a for a in self.assets.values() if a.name==name]
    def register_version(self,name,kind,path="",metadata=None):
        v=len(self.versions(name))+1
        return self.add(Asset(name,kind,path,version=v,metadata=metadata or {}))
