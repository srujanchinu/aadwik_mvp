from dataclasses import dataclass

@dataclass
class CostBudget:
    limit:float=0.0
    spent:float=0.0
    currency:str="USD"

    @property
    def remaining(self): return max(0.0,self.limit-self.spent)

    def can_spend(self,amount): return float(amount)>=0 and self.spent+float(amount)<=self.limit

    def spend(self,amount):
        amount=float(amount)
        if not self.can_spend(amount): raise ValueError("Cost protection budget exceeded")
        self.spent+=amount
        return self.spent

def estimate_cost(units,unit_cost): return max(0.0,float(units)*float(unit_cost))
