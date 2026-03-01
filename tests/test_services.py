import pandas as pd
from io import BytesIO
from fastapi import UploadFile
from app.services import _normalize_plan, _normalize_actual, _normalize_prescription, _find_discrepancies, _evaluate_prescriptions


def make_upload(dataframe: pd.DataFrame, name: str) -> UploadFile:
    buffer = BytesIO()
    dataframe.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    return UploadFile(filename=name, file=buffer)


def test_simple_reconciliation():
    plan = pd.DataFrame({
        "patient_id": ["p1", "p2"],
        "date": ["2026-01-01", "2026-01-02"],
        "hours": [1.0, 2.0],
        "tariff": ["A", "B"],
    })
    actual = pd.DataFrame({
        "patient_id": ["p1", "p2"],
        "date": ["2026-01-01", "2026-01-02"],
        "billed_hours": [1.0, 1.5],
        "tariff": ["A", "B"],
    })
    presc = pd.DataFrame({
        "patient_id": ["p1"],
        "period_start": ["2026-01-01"],
        "period_end": ["2026-06-30"],
        "authorized_hours": [100],
    })

    pfile = make_upload(plan, "plan.xlsx")
    afile = make_upload(actual, "actual.xlsx")
    prfile = make_upload(presc, "presc.xlsx")

    # normalize
    plan_n = _normalize_plan(pd.read_excel(pfile.file))
    actual_n = _normalize_actual(pd.read_excel(afile.file))
    presc_n = _normalize_prescription(pd.read_excel(prfile.file))

    # find discrepancies
    issues = _find_discrepancies(plan_n, actual_n)
    assert len(issues) == 1
    assert issues[0].issue == "duration_mismatch"

    # evaluate prescriptions
    statuses = _evaluate_prescriptions(presc_n, actual_n)
    # only patient p1 has actual hours of 1.0 within the prescription period
    assert statuses[0].used_hours == 1.0
    assert statuses[0].status == "ok"
