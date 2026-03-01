"""Generate sample Excel exports for plan, actual and prescription data.

Run this script from the project root to create files in a `samples/` folder.
"""
import pandas as pd
import os

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "samples")

os.makedirs(SAMPLE_DIR, exist_ok=True)

# sample dataframes
df_plan = pd.DataFrame({
    "patient_id": ["p1", "p2", "p3"],
    "service_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
    "hours": [1.0, 2.5, 3.0],
    "tariff": ["A", "B", "A"],
})
df_actual = pd.DataFrame({
    "patient_id": ["p1", "p2", "p3", "p4"],
    "service_date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
    "billed_hours": [1.0, 2.0, 3.0, 4.0],
    "tariff": ["A", "B", "A", "C"],
})
df_presc = pd.DataFrame({
    "patient_id": ["p1", "p2"],
    "period_start": ["2026-01-01", "2026-01-01"],
    "period_end": ["2026-06-30", "2026-06-30"],
    "authorized_hours": [100, 50],
})

plan_file = os.path.join(SAMPLE_DIR, "plan.xlsx")
actual_file = os.path.join(SAMPLE_DIR, "actual.xlsx")
presc_file = os.path.join(SAMPLE_DIR, "prescription.xlsx")

for df, path in [(df_plan, plan_file), (df_actual, actual_file), (df_presc, presc_file)]:
    df.to_excel(path, index=False, engine="openpyxl")
    print(f"created {path}")
