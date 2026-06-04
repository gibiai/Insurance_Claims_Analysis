# src/visualization.py
# Creates 3 charts + 1 animated GIF for the insurance analysis
 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import os
 
plt.rcParams["figure.dpi"]       = 100
plt.rcParams["figure.facecolor"] = "white"
sns.set_style("whitegrid")
 
# consistent color palette across all charts
COLORS = {
    "smoker":     "#E63946",
    "non_smoker": "#2A9D8F",
    "accent":     "#457B9D",
    "warn":       "#E9C46A",
}

def make_all_charts(df: pd.DataFrame, output_dir: str = "output") -> None:
    # generate all charts and save them to the output directory
    os.makedirs(output_dir, exist_ok=True)
    
 # ── Chart 1: average charge by age band, split by smoker ─────────────
    # grouped bar chart — shows age AND smoker effect together
    fig, ax = plt.subplots(figsize=(10, 5))
 
    age_smoker = (
        df.groupby(["age_band", "smoker"], observed=True)["charges"]
        .mean()
        .unstack()   # turns smoker values into columns for grouped bars
    )
 
    age_smoker.plot(
        kind="bar", ax=ax,
        color=[COLORS["non_smoker"], COLORS["smoker"]],
        width=0.75,
    )
 
    ax.set_title("Average Charge by Age Band and Smoker Status",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Age Band")
    ax.set_ylabel("Average Charge (USD)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend(title="Smoker", labels=["No", "Yes"])
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/01_charge_by_age_smoker.png", bbox_inches="tight")
    plt.close()
    print("Chart 1 saved")
 
    # ── Chart 2: charge distribution by smoker (violin) ──────────────────
    # violin shows the full distribution shape, not just averages
    fig, ax = plt.subplots(figsize=(8, 5))
 
    sns.violinplot(
        data=df, x="smoker", y="charges",
        hue="smoker",
        palette=[COLORS["non_smoker"], COLORS["smoker"]],
        legend=False, ax=ax,
    )
 
    ax.set_title("Charge Distribution by Smoker Status",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Smoker")
    ax.set_ylabel("Charges (USD)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    plt.savefig(f"{output_dir}/02_distribution_by_smoker.png", bbox_inches="tight")
    plt.close()
    print("Chart 2 saved")
 
    # ── Chart 3: BMI vs charges scatter, colored by smoker ───────────────
    # reveals that high BMI + smoker = highest charges
    fig, ax = plt.subplots(figsize=(10, 5))
 
    for smoker_val, color in [("no", COLORS["non_smoker"]), ("yes", COLORS["smoker"])]:
        subset = df[df["smoker"] == smoker_val]
        ax.scatter(subset["bmi"], subset["charges"],
                   c=color, alpha=0.5, s=20,
                   label="Smoker" if smoker_val == "yes" else "Non-smoker")
 
    ax.set_title("BMI vs Charges by Smoker Status",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("BMI")
    ax.set_ylabel("Charges (USD)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.axvline(30, color="gray", linestyle="--", linewidth=0.8, label="Obesity threshold (30)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/03_bmi_vs_charges.png", bbox_inches="tight")
    plt.close()
    print("Chart 3 saved")
 
    # ── Animated GIF: average charge building up by age band ─────────────
    # bars appear progressively from youngest to oldest age band
    fig, ax = plt.subplots(figsize=(10, 5))
 
    age_avg = df.groupby("age_band", observed=True)["charges"].mean()
    age_bands = list(age_avg.index)
    values    = list(age_avg.values)
 
    def update(frame):
        ax.clear()
        # show bars up to the current frame
        current_bands  = age_bands[:frame + 1]
        current_values = values[:frame + 1]
 
        ax.bar(current_bands, current_values, color=COLORS["accent"])
 
        # add value labels
        for i, val in enumerate(current_values):
            ax.text(i, val + 300, f"${val:,.0f}", ha="center", fontsize=10)
 
        ax.set_title("Average Charge Rising with Age",
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Age Band")
        ax.set_ylabel("Average Charge (USD)")
        ax.set_xlim(-0.5, len(age_bands) - 0.5)
        ax.set_ylim(0, max(values) * 1.15)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        plt.tight_layout()
 
    ani = animation.FuncAnimation(
        fig, update, frames=len(age_bands), interval=800, repeat=False
    )
    ani.save(f"{output_dir}/04_charge_by_age.gif", writer="pillow", fps=1.5)
    plt.close()
    print("GIF saved")
 
    print(f"\nAll visuals saved to {output_dir}/")
 
 
if __name__ == "__main__":
    df = pd.read_csv("data/insurance_clean.csv")
    make_all_charts(df)
 