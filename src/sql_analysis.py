# src/sql_analysis.py
# SQL analysis using an in-memory SQLite database
#
# SQLite runs entirely in RAM — no server, no file saved.
# We load the DataFrame as a SQL table and run real queries on it.

import pandas as pd
import sqlite3

def run_sql_analysis(df: pd.DataFrame) -> dict:
    # run sql queries on the insurance data using in-memory SQLite
    # returns a dict of a result DataFrames
    conn = sqlite3.connect(":memory:")
    
    # load the DataFrame into SQLite as atable named "insurance"
    df.to_sql("insurance", conn, index=False, if_exists="replace")
    
    print("-" * 40)
    print("SQL Analysis")
    print("-" * 40)
    
    # query 1: average charge by smoker status and region
    # combine two group by columns to find the highest-risk combination
    # round keeps the output readable
    q1 = pd.read_sql("""
        SELECT
            smoker,
            region,
            COUNT(*)              AS policy_count,
            ROUND(AVG(charges), 0) AS avg_charge
        FROM insurance
        GROUP BY smoker, region
        ORDER BY avg_charge DESC
    """, conn)
    print("\nQ1 — Average charge by smoker status and region:")
    print(q1.to_string(index=False))

    # query 2: high-cost age bands above portfolio average
    # case creates age bands inside SQL (like pd.cut but in a query)
    # having filters groups whose average exceeds the overall average
    # the subquery computes that overall average dynamically
    q2 = pd.read_sql("""
        SELECT
            CASE
                WHEN age < 30 THEN '18-29'
                WHEN age < 40 THEN '30-39'
                WHEN age < 50 THEN '40-49'
                ELSE '50-64'
            END AS age_band,
            COUNT(*)               AS policy_count,
            ROUND(AVG(charges), 0)  AS avg_charge
        FROM insurance
        GROUP BY age_band
        HAVING AVG(charges) > (SELECT AVG(charges) FROM insurance)
        ORDER BY avg_charge DESC
    """, conn)
 
    print("\nQ2 — Age bands costing above portfolio average:")
    print(q2.to_string(index=False))
    
    conn.close()
    
    return {"by_smoker_region": q1, "high_cost_age_bands": q2}

if __name__ == "__main__":
    df = pd.read_csv("data/insurance.csv")
    run_sql_analysis(df)