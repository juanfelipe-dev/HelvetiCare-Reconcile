from io import BytesIO
import pandas as pd
from .schemas import ReconciliationResult


def result_to_excel(result: ReconciliationResult) -> BytesIO:
    # build a simple Excel file with discrepancies and prescription statuses
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # discrepancies
        if result.discrepancies:
            df1 = pd.DataFrame([d.model_dump() for d in result.discrepancies])
        else:
            df1 = pd.DataFrame(columns=["patient_id", "date", "planned_hours", "actual_hours", "tariff", "issue"])
        df1.to_excel(writer, index=False, sheet_name="discrepancies")

        # prescription statuses
        if result.prescription_statuses:
            df2 = pd.DataFrame([p.model_dump() for p in result.prescription_statuses])
        else:
            df2 = pd.DataFrame(columns=["patient_id", "period_start", "period_end", "authorized_hours", "used_hours", "status"])
        df2.to_excel(writer, index=False, sheet_name="prescriptions")

        # summary
        summary_df = pd.DataFrame([result.summary])
        summary_df.to_excel(writer, index=False, sheet_name="summary")

    output.seek(0)
    return output
