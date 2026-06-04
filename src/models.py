# src/models.py 
# OOP - 3 classes: Policyholder, Policy, InsurancePortfolio

from dataclasses import dataclass, field

@dataclass
class Policyholder:
    """ single insured person with their risk attributes """
    age: int
    sex: str
    bmi: float
    childer: int
    smoker: bool
    region: str
    
    @property
    def bmi_category(self) -> str:
        # standar WHO BMI bands, used for risk assessment
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"
        
    @property
    def age_band(self) -> str:
        # acturial age bands for grouping risk
        if self.age < 30:
            return "18-29"
        elif self.age < 40:
            return "30-39"
        elif self.age < 50:
            return "40-49"
        else:
            return "50-64"
    
    @property
    def risk_flags(self) -> int:
        # simple risk score: count how many risk factors apply
        # used to quickly segment high-risk policyholders
        flags = 0
        if self.smoker:
            flags += 1
        if self.bmi >= 30: # obese
            flags += 1
        if self.age >= 50: # older age band
            flags += 1
        return flags
    
@dataclass
class Policy:
    """An insurance policy linking a policyholder to their annual charge."""
    policy_id: str
    holder: Policyholder
    annual_charge: float
    
    @property
    def is_high_cost(self) -> bool:
        # a policy is high cost if charge exceeds the portfolio benchmark
        # benchmark passed in at portfolio level — here we use a fixed threshold
        return self.annual_charge > 13270 # dataset mean charge

class InsurancePortfolio:
    """Manages a collection of policies and computes aggregate metrics."""
    def ___init__(self):
        self.policies: list[Policy] = []
    
    def add_policy(self, policy: Policy) -> None:
        """Add a single policy to the portfolio."""
        self.policies.append(policy)
        
    @property
    def total_policies(self) -> int:
        return len(self.policies)
    
    @property
    def total_charges(self) -> float:
        """Sum of all annual charges — total expected payout."""
        return sum(p.annual_charge for p in self.policies)
    
    @property
    def average_charge(self) -> float:
        """Average charge per policy — the baseline premium reference."""
        if self.total_policies == 0:
            return 0.0
        return self.total_charges / self.total_policies 
    
    def average_charge_by_group(self, attribute: str) -> dict:
        """
        Average charge grouped by a policyholder attribute.
        Example: average_charge_by_group("smoker") → {True: 32050, False: 8434}
        """
        groups: dict = {}
        counts: dict = {}
        
        for policy in self.policies:
            # getattr reads the attribute dynamically by its name
            key = getattr(policy.holder, attribute)
            groups[key] = groups.get(key, 0) + policy.annual_charge
            counts[key] = counts.get(key, 0) + 1
            
        # convert sums to averages
        return {k: round(groups[k] / counts[k], 2) for k in groups}
    
    def high_risk_policies(self, min_flags: int = 2) -> list[Policy]:
        """Return policies whose holders have at least min_flags risk factors."""
        return [p for p in self.policies if p.holder.risk_flags >= min_flags]
    
    @classmethod
    def from_dataframe(cls, df) -> "InsurancePortfolio":
        """
        Build a portfolio directly from a pandas DataFrame.
        classmethod = alternative constructor — creates the object
        from a different input than the default __init__.
        """
        portfolio = cls()   # cls() is the same as InsurancePortfolio()
 
        for i, row in df.iterrows():
            holder = Policyholder(
                age      = int(row["age"]),
                sex      = row["sex"],
                bmi      = float(row["bmi"]),
                children = int(row["children"]),
                smoker   = (row["smoker"] == "yes"),
                region   = row["region"],
            )
            policy = Policy(
                policy_id     = f"POL{i+1:04d}",
                holder        = holder,
                annual_charge = float(row["charges"]),
            )
            portfolio.add_policy(policy)
 
        return portfolio
    
# quick self test when run directly
if __name__ == "__main__":
    import pandas as pd 
        
    df = pd.read_csv("data/insurance.csv")
    portfolio = InsurancePortfolio.from_dataframe(df)
        
    print(f"Total policies:  {portfolio.total_policies}")
    print(f"Average charge:  ${portfolio.average_charge:,.2f}")
    print(f"\nAvg charge by smoker: {portfolio.average_charge_by_group('smoker')}")
    print(f"Avg charge by region: {portfolio.average_charge_by_group('region')}")
    print(f"\nHigh-risk policies (2+ flags): {len(portfolio.high_risk_policies())}")