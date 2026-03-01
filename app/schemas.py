from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Discrepancy(BaseModel):
    patient_id: str
    date: str
    planned_hours: Optional[float]
    actual_hours: Optional[float]
    tariff: Optional[str]
    issue: str  # e.g. "planned_not_delivered", "billed_not_planned", "duration_mismatch"


class PrescriptionStatus(BaseModel):
    patient_id: str
    period_start: str
    period_end: str
    authorized_hours: float
    used_hours: float
    status: str  # "ok", "near_limit", "exceeded"


class ReconciliationResult(BaseModel):
    discrepancies: List[Discrepancy]
    prescription_statuses: List[PrescriptionStatus]
    summary: Dict[str, Any]
