from dataclasses import dataclass, field
@dataclass
class GateResult:
    name:str; passed:bool; message:str=''; metrics:dict=field(default_factory=dict)
@dataclass
class QualityReport:
    passed:bool; results:list; score:float
class QualityGate:
    def __init__(self,name,check): self.name=name; self.check=check
    def run(self,context):
        r=self.check(context)
        if not isinstance(r,GateResult): raise TypeError('Quality gate must return GateResult')
        return r
def run_quality_gates(context,gates):
    results=[g.run(context) for g in gates]
    score=(sum(r.passed for r in results)/len(results)*100) if results else 100
    return QualityReport(all(r.passed for r in results),results,score)
def required_field_gate(name,field_name):
    return QualityGate(name,lambda c:GateResult(name,bool(c.get(field_name)),f'{field_name} check'))
