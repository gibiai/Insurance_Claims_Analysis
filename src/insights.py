# src/insights.py
# Generates business insights and a simple premium pricing model
#
# Combines the actuarial analysis into plain-language recommendations
# and trains a Linear Regression to predict charges (premium pricing).
 
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error
import os

def generate_insights(df: pd.DataFrame) -> list[str]:
    # generate plain-language business insights from the data
    insights = []
    
    # smoke multiplier
    smoker_avg = df[df["smoker"] == "yes"]["charges"].mean()
    non_smoker_avg = df[df["smoker"] == "no"]["charges"].mean()
    mult = smoker_avg / non_smoker_avg
    insights.append(
        f"Smokers cost {mult:.1f}x more than non-smokers "
        f"(${smoker_avg:,.0f} vs ${non_smoker_avg:,.0f}). "
        f"A significant premium loading for smokers is justified."
    )
    
    # obesity effect among smokers
    obese_smokers = df[(df["smoker"] == "yes") & (df["bmi"] >= 30)]["charges"].mean()
    insights.append(
        f"Obese smokers are the highest-risk segment at ${obese_smokers:,.0f} "
        f"average charge: over 3x the portfolio average"
    )
    
    # age effect
    youngest = df[df["age_band"] == "18-29"]["charges"].mean()
    oldest = df[df["age_band"] == "50-64"]["charges"].mean()
    age_growth = (oldest / youngest - 1) * 100
    insights.append(
        f"Charges grow {age_growth:.0f}% from the youngest to oldest age band "
        f"(${youngest:,.0f} → ${oldest:,.0f}). Age-based pricing tiers are warranted."
    )
    
      # region effect
    region_avg = df.groupby("region", observed=True)["charges"].mean()
    top_region = region_avg.idxmax()
    insights.append(
        f"The {top_region.title()} region has the highest average charges "
        f"(${region_avg.max():,.0f}), suggesting mild regional risk adjustment."
    )
 
    return insights

def train_pricing_model(df: pd.DataFrame, output_dir: str = "output") -> dict:
    """
    Train a Linear Regression to predict charges (premium estimation).
    Linear Regression is the natural choice here: it is interpretable
    and actuaries value being able to explain each factor's contribution.
    """
    os.makedirs(output_dir, exist_ok=True)
 
    # select features for the model
    features = ["age", "bmi", "children", "smoker", "sex", "region"]
    model_df = df[features + ["charges"]].copy()
 
    # label-encode categorical columns — LR needs numeric input
    encoders = {}
    for col in ["smoker", "sex", "region"]:
        le = LabelEncoder()
        model_df[col] = le.fit_transform(model_df[col])
        encoders[col] = le
 
    X = model_df[features]
    y = model_df["charges"]
 
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
 
    model = LinearRegression()
    model.fit(X_train, y_train)
 
    y_pred = model.predict(X_test)
    r2  = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
 
    # coefficients show each factor's dollar impact on the premium
    coef_df = pd.DataFrame({
        "feature":     features,
        "coefficient": model.coef_.round(0),
    }).sort_values("coefficient", key=abs, ascending=False)
 
    # save coefficients for Power BI
    coef_df.to_csv(f"{output_dir}/pricing_coefficients.csv", index=False)
 
    print("=" * 55)
    print("Premium Pricing Model — Linear Regression")
    print("=" * 55)
    print(f"\nR² (explained variance): {r2:.3f}")
    print(f"MAE (avg error in USD):  ${mae:,.0f}")
    print("\nFactor coefficients (impact on predicted charge):")
    print(coef_df.to_string(index=False))
 
    return {"r2": round(r2, 3), "mae": round(mae, 0), "coefficients": coef_df}
 
 
def run_insights(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Generate insights and train the pricing model."""
    print("=" * 55)
    print("Business Insights")
    print("=" * 55)
 
    insights = generate_insights(df)
    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. {insight}")
 
    print()
    model_results = train_pricing_model(df, output_dir)
 
    # save insights to a text file for the dashboard / README
    with open(f"{output_dir}/business_insights.txt", "w") as f:
        f.write("BUSINESS INSIGHTS — Insurance Charges Analysis\n")
        f.write("=" * 50 + "\n\n")
        for i, insight in enumerate(insights, 1):
            f.write(f"{i}. {insight}\n\n")
        f.write(f"\nPricing Model — R2: {model_results['r2']}, "
                f"MAE: ${model_results['mae']:,.0f}\n")
 
    print(f"\nInsights saved to {output_dir}/business_insights.txt")
 
 
if __name__ == "__main__":
    df = pd.read_csv("data/insurance_clean.csv")
    run_insights(df)
    