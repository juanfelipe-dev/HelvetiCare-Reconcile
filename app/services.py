import pandas as pd
from fastapi import UploadFile
from io import BytesIO
from typing import List
from .schemas import ReconciliationResult, Discrepancy, PrescriptionStatus


async def reconcile_files(plan_file: UploadFile, actual_file: UploadFile, prescription_file: UploadFile) -> ReconciliationResult:
    # read in-memory
    plan_df = _read_excel(plan_file)
    actual_df = _read_excel(actual_file)
    presc_df = _read_excel(prescription_file)

    # simple normalization
    plan_df = _normalize_plan(plan_df)
    actual_df = _normalize_actual(actual_df)
    presc_df = _normalize_prescription(presc_df)

    discrepancies = _find_discrepancies(plan_df, actual_df)
    prescription_statuses = _evaluate_prescriptions(presc_df, actual_df)

    summary = {
        "total_planned": plan_df.shape[0],
        "total_actual": actual_df.shape[0],
        "discrepancies": len(discrepancies),
        "prescriptions_evaluated": len(prescription_statuses),
    }

    return ReconciliationResult(
        discrepancies=discrepancies,
        prescription_statuses=prescription_statuses,
        summary=summary,
    )


def _read_excel(upload_file: UploadFile) -> pd.DataFrame:
    contents = upload_file.file.read()
    try:
        df = pd.read_excel(BytesIO(contents), engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Unable to read Excel file {upload_file.filename}: {e}")
    return df


def _normalize_plan(df: pd.DataFrame) -> pd.DataFrame:
    # Expect columns: patient_id, date, hours, tariff
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    # rename common alternatives
    df = df.rename(columns={
        "patient": "patient_id",
        "service_date": "date",
        "duration": "hours",
    })
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["hours"] = pd.to_numeric(df["hours"], errors="coerce").fillna(0)
    return df[["patient_id", "date", "hours", "tariff"]]


def _normalize_actual(df: pd.DataFrame) -> pd.DataFrame:
    # Expect columns: patient_id, date, billed_hours, tariff
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    df = df.rename(columns={
        "patient": "patient_id",
        "service_date": "date",
        "duration": "billed_hours",
        "hours": "billed_hours",
    })
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["billed_hours"] = pd.to_numeric(df["billed_hours"], errors="coerce").fillna(0)
    return df[["patient_id", "date", "billed_hours", "tariff"]]


def _normalize_prescription(df: pd.DataFrame) -> pd.DataFrame:
    # Expect columns: patient_id, period_start, period_end, authorized_hours
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    df = df.rename(columns={
        "patient": "patient_id",
        "start": "period_start",
        "end": "period_end",
        "authorized": "authorized_hours",
    })
    df["period_start"] = pd.to_datetime(df["period_start"]).dt.date
    df["period_end"] = pd.to_datetime(df["period_end"]).dt.date
    df["authorized_hours"] = pd.to_numeric(df["authorized_hours"], errors="coerce").fillna(0)
    return df[["patient_id", "period_start", "period_end", "authorized_hours"]]


def _find_discrepancies(plan_df: pd.DataFrame, actual_df: pd.DataFrame) -> List[Discrepancy]:
    # merge on patient, date, tariff for simple matching
    merged = pd.merge(plan_df, actual_df, how="outer", on=["patient_id", "date", "tariff"], suffixes=("_plan", "_actual"))
    issues: List[Discrepancy] = []
    for _, row in merged.iterrows():
        if pd.isna(row.get("hours")) and not pd.isna(row.get("billed_hours")):
            issues.append(Discrepancy(
                patient_id=str(row["patient_id"]),
                date=str(row["date"]),
                planned_hours=None,
                actual_hours=float(row["billed_hours"]),
                tariff=row.get("tariff"),
                issue="billed_not_planned"
            ))
        elif not pd.isna(row.get("hours")) and pd.isna(row.get("billed_hours")):
            issues.append(Discrepancy(
                patient_id=str(row["patient_id"]),
                date=str(row["date"]),
                planned_hours=float(row["hours"]),
                actual_hours=None,
                tariff=row.get("tariff"),
                issue="planned_not_delivered"
            ))
        elif not pd.isna(row.get("hours")) and not pd.isna(row.get("billed_hours")):
            if abs(row["hours"] - row["billed_hours"]) > 0.01:
                issues.append(Discrepancy(
                    patient_id=str(row["patient_id"]),
                    date=str(row["date"]),
                    planned_hours=float(row["hours"]),
                    actual_hours=float(row["billed_hours"]),
                    tariff=row.get("tariff"),
                    issue="duration_mismatch"
                ))
    return issues


def _evaluate_prescriptions(presc_df: pd.DataFrame, actual_df: pd.DataFrame) -> List[PrescriptionStatus]:
    statuses: List[PrescriptionStatus] = []
    # iterate over prescriptions
    for _, pres in presc_df.iterrows():
        patient = pres["patient_id"]
        start = pres["period_start"]
        end = pres["period_end"]
        mask = (
            (actual_df["patient_id"] == patient) &
            (actual_df["date"] >= start) &
            (actual_df["date"] <= end)
        )
        used = actual_df.loc[mask, "billed_hours"].sum()
        auth = pres["authorized_hours"]
        status = "ok"
        if used > auth:
            status = "exceeded"
        elif used > auth * 0.9:
            status = "near_limit"
        statuses.append(PrescriptionStatus(
            patient_id=str(patient),
            period_start=str(start),
            period_end=str(end),
            authorized_hours=float(auth),
            used_hours=float(used),
            status=status
        ))
    return statuses
