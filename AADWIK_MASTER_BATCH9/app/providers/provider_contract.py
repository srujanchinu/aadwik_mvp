from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ProviderResult:
    success:bool
    output_path:str=""
    provider:str=""
    error:str|None=None
    metadata:dict|None=None

class VideoProviderContract(ABC):
    name="base"
    @abstractmethod
    def generate_video(self,prompt,output_path,aspect_ratio="16:9",style=None,**kwargs):
        raise NotImplementedError
