# src/analysis.py
# Actuarial analysis — the three pillars: frequency, severity, and cost ratios
#
# In real actuarial work these metrics drive premium pricing decisions.
# Here we adapt them to a health insurance charges dataset.
import pandas as pd

def charge_summary(df: pd.DataFrame) -> dict:
    # overall portfolio metrics - the headline numbers
    return {
        "total_policies": len(df),
        "total_charges": round(df["charges"].sum(), 0),
        "average_charge": round(df["charges"].mean(), 0),
        "median_charge": round(df["charges"].median(), 0),
        "max_charge": round(df["charges"].max(), 0)
    }
    
def average_by_factor(df: pd.DataFrame, factor: str) -> pd.DataFrame:
# average charge grouped by a single risk factor
# returns a tidy DataFrame ready for charting or export
    result =(
        df.groupby(factor, observed=True)["charges"]
        .agg(avg_charge="mean", policy_count="count")
        .round(0)
        .reset_index()
        .sort_values("avg_charge", ascending=False)
    )
    return result

def smoker_risk_multiplier(df: pd.DataFrame) -> float:
    # how many times more a smoker costs vs a non-smoker
    # this is the single strongest pricing signal in the dataset
    smoker_avg = df[df["smoker"] == "yes"]["charges"].mean()
    non_smoker_avg = df[df["smoker"] == "no"]["charges"].mean()
    return round(smoker_avg / non_smoker_avg, 2)

def risk_loading_table(df: pd.DataFrame) -> pd.DataFrame:
# build a simplified "risk loading" table: by how much each segment's
# average charge exceeds the overall portfolio average
# a loading > 1.0 means the segment cost more than average and would
# warrant a higher premium
# < 1.0 means it costs less
    overall_avg = df["charges"].mean()
 
    rows = []
    # check each smoker / bmi_category combination
    for smoker in ["yes", "no"]:
        for bmi_cat in df["bmi_category"].dropna().unique():
            subset = df[(df["smoker"] == smoker) & (df["bmi_category"] == bmi_cat)]
            if len(subset) == 0:
                continue
            seg_avg = subset["charges"].mean()
            rows.append({
                "smoker":       smoker,
                "bmi_category": bmi_cat,
                "policy_count": len(subset),
                "avg_charge":   round(seg_avg, 0),
                "risk_loading": round(seg_avg / overall_avg, 2),
            })
 
    table = pd.DataFrame(rows).sort_values("risk_loading", ascending=False)
    return table.reset_index(drop=True)

def run_full_analysis(df: pd.DataFrame) -> dict:
    # run all analyses and return as a dictionary
    print("-" * 40)
    print("Actuarial Analysis")
    print("-" * 40)
    
    summary = charge_summary(df)
    print("\n--- Portfolio Summary ---")
    for key, value in summary.items():
        print(f" {key:18s}: {value:,.0f}" if isinstance(value, (int, float)) else f" {key}: {value}")
        
    multiplier = smoker_risk_multiplier(df)
    print(f"\n--- Smoker Risk Multiplier: {multiplier}x ---")
    
    print("\n--- Average Charge by Age Band ---")
    age_table = average_by_factor(df, "age_band")
    print(age_table.to_string(index=False))
    
    print("\n--- Risk Loading Table (smoker x BMI) ---")
    loading = risk_loading_table(df)
    print(loading.to_string(index=False))
 
    return {
        "summary":      summary,
        "multiplier":   multiplier,
        "by_age":       age_table,
        "by_region":    average_by_factor(df, "region"),
        "by_bmi":       average_by_factor(df, "bmi_category"),
        "risk_loading": loading,
    }
    
if __name__ == "__main__":
    df = pd.read_csv("data/insurance_clean.csv")
    run_full_analysis(df)
    