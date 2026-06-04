# main.py
# Entry point — runs the full insurance analysis pipeline
 
import os
import sys
import pandas as pd
 
# add src/ to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
 
from analysis import run_full_analysis
from sql_analysis import run_sql_analysis
from visualization import make_all_charts
from insights import run_insights
from excel_report import build_excel_report
 
 
def main():
    # work from the project root so all relative paths line up
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs("output", exist_ok=True)
 
    print("\n" + "#" * 55)
    print("  INSURANCE CHARGES ANALYSIS — Full Pipeline")
    print("#" * 55)
 
    # load the cleaned dataset produced by the notebook
    # falls back to raw data if the clean file is not present yet
    clean_path = "data/insurance_clean.csv"
    if os.path.exists(clean_path):
        df = pd.read_csv(clean_path)
    else:
        print("\nClean dataset not found — building features from raw data.")
        df = pd.read_csv("data/insurance.csv")
        df["age_band"] = pd.cut(df["age"], bins=[17, 29, 39, 49, 64],
                                labels=["18-29", "30-39", "40-49", "50-64"])
        df["bmi_category"] = pd.cut(df["bmi"], bins=[0, 18.5, 25, 30, 100],
                                    labels=["Underweight", "Normal", "Overweight", "Obese"])
 
    print(f"\nLoaded {len(df)} policies.\n")
 
    # run each stage of the pipeline
    run_full_analysis(df)
    print()
    run_sql_analysis(df)
    print()
    make_all_charts(df)
    print()
    run_insights(df)
    print()
    build_excel_report(df)
 
    print("\n" + "#" * 55)
    print("  Pipeline complete — see output/ for all results")
    print("#" * 55 + "\n")
 
 
if __name__ == "__main__":
    main()