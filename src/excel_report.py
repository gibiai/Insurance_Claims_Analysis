# src/excel_report.py
# Generates a professional Excel summary report with openpyxl
# Includes a styled summary table and a pivot-style risk loading matrix

import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows


def build_excel_report(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Create a formatted Excel report with summary metrics and risk table."""
    os.makedirs(output_dir, exist_ok=True)

    wb = Workbook()

    # ── styling helpers ───────────────────────────────────────────────
    header_fill = PatternFill(start_color="1A1D27", end_color="1A1D27", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    title_font  = Font(color="1A1D27", bold=True, size=14)
    center      = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style="thin", color="DDDDDD"),
        right=Side(style="thin", color="DDDDDD"),
        top=Side(style="thin", color="DDDDDD"),
        bottom=Side(style="thin", color="DDDDDD"),
    )

    # ═══ SHEET 1: Summary ═══
    ws1 = wb.active
    ws1.title = "Summary"

    ws1["A1"] = "Insurance Portfolio — Summary Report"
    ws1["A1"].font = title_font
    ws1.merge_cells("A1:C1")

    # summary metrics
    summary_data = [
        ["Metric", "Value", ""],
        ["Total Policies", len(df), ""],
        ["Total Charges", f"${df['charges'].sum():,.0f}", ""],
        ["Average Charge", f"${df['charges'].mean():,.0f}", ""],
        ["Median Charge", f"${df['charges'].median():,.0f}", ""],
        ["Smoker Multiplier",
         f"{df[df.smoker=='yes']['charges'].mean() / df[df.smoker=='no']['charges'].mean():.1f}x", ""],
    ]

    for r_idx, row in enumerate(summary_data, start=3):
        for c_idx, value in enumerate(row, start=1):
            cell = ws1.cell(row=r_idx, column=c_idx, value=value)
            cell.border = thin_border
            if r_idx == 3:  # header row
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center

    ws1.column_dimensions["A"].width = 22
    ws1.column_dimensions["B"].width = 18
    ws1.column_dimensions["C"].width = 5

    # ═══ SHEET 2: Risk Loading Matrix ═══
    ws2 = wb.create_sheet("Risk Loading")

    ws2["A1"] = "Risk Loading by Smoker Status and BMI Category"
    ws2["A1"].font = title_font
    ws2.merge_cells("A1:E1")

    # build risk loading table
    overall_avg = df["charges"].mean()
    rows = []
    for smoker in ["yes", "no"]:
        for bmi_cat in df["bmi_category"].dropna().unique():
            subset = df[(df["smoker"] == smoker) & (df["bmi_category"] == bmi_cat)]
            if len(subset) == 0:
                continue
            seg_avg = subset["charges"].mean()
            rows.append({
                "Smoker":       smoker,
                "BMI Category": bmi_cat,
                "Policies":     len(subset),
                "Avg Charge":   round(seg_avg, 0),
                "Risk Loading": round(seg_avg / overall_avg, 2),
            })
    loading_df = pd.DataFrame(rows).sort_values("Risk Loading", ascending=False)

    # write the table starting at row 3
    start_row = 3
    for c_idx, col_name in enumerate(loading_df.columns, start=1):
        cell = ws2.cell(row=start_row, column=c_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center
        cell.border = thin_border

    for r_idx, (_, row) in enumerate(loading_df.iterrows(), start=start_row + 1):
        for c_idx, value in enumerate(row, start=1):
            cell = ws2.cell(row=r_idx, column=c_idx, value=value)
            cell.border = thin_border
            cell.alignment = center
            # highlight high risk loading rows in red
            if loading_df.columns[c_idx-1] == "Risk Loading" and value > 2.0:
                cell.fill = PatternFill(start_color="E63946", end_color="E63946", fill_type="solid")
                cell.font = Font(color="FFFFFF", bold=True)

    for col in ["A", "B", "C", "D", "E"]:
        ws2.column_dimensions[col].width = 16

    # save
    path = f"{output_dir}/insurance_summary.xlsx"
    wb.save(path)
    print(f"Excel report saved: {path}")


if __name__ == "__main__":
    df = pd.read_csv("data/insurance_clean.csv")
    build_excel_report(df)