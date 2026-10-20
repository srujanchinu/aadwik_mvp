from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class ExperimentVariant:
    name:str
    configuration:dict=field(default_factory=dict)
    variant_id:str=field(default_factory=lambda:"variant_"+uuid4().hex)

@dataclass
class Experiment:
    name:str
    hypothesis:str
    variants:list=field(default_factory=list)
    status:str="DRAFT"
    experiment_id:str=field(default_factory=lambda:"exp_"+uuid4().hex)

    def add_variant(self,name,configuration=None):
        v=ExperimentVariant(name,configuration or {})
        self.variants.append(v)
        return v

    def start(self):
        if len(self.variants)<2:
            raise ValueError("Experiment needs at least two variants")
        self.status="RUNNING"; return self
