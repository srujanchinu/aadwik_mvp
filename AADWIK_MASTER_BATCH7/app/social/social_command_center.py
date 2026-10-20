from dataclasses import dataclass, field
from uuid import uuid4

SUPPORTED_PLATFORMS=("Facebook","Instagram","Threads","YouTube")

@dataclass
class PlatformAccount:
    platform:str
    account_name:str
    permissions:list=field(default_factory=list)
    connected:bool=True
    account_id:str=field(default_factory=lambda:"acct_"+uuid4().hex)

class SocialCommandCenter:
    def __init__(self): self.accounts={}
    def connect(self,platform,account_name,permissions=None):
        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError("Unsupported platform")
        a=PlatformAccount(platform,account_name,permissions or [])
        self.accounts[a.account_id]=a
        return a
    def disconnect(self,account_id):
        if account_id in self.accounts: self.accounts[account_id].connected=False
    def capabilities(self,account_id):
        a=self.accounts[account_id]
        return {"platform":a.platform,"connected":a.connected,"permissions":list(a.permissions)}
