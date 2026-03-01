from fastapi.testclient import TestClient
import os
from app.main import app

client = TestClient(app)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "samples")


def test_reconciliation_endpoint():
    files = {
        "plan_file": open(os.path.join(SAMPLE_DIR, "plan.xlsx"), "rb"),
        "actual_file": open(os.path.join(SAMPLE_DIR, "actual.xlsx"), "rb"),
        "prescription_file": open(os.path.join(SAMPLE_DIR, "prescription.xlsx"), "rb"),
    }
    response = client.post("/reconcile", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "discrepancies" in data
    assert "prescription_statuses" in data
    assert data["summary"]["total_planned"] == 3
    # clean up file handles
    for f in files.values():
        f.close()


def test_reconcile_download():
    files = {
        "plan_file": open(os.path.join(SAMPLE_DIR, "plan.xlsx"), "rb"),
        "actual_file": open(os.path.join(SAMPLE_DIR, "actual.xlsx"), "rb"),
        "prescription_file": open(os.path.join(SAMPLE_DIR, "prescription.xlsx"), "rb"),
    }
    response = client.post("/reconcile?download=true", files=files)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/vnd.openxmlformats")
    # verify that the bytes returned actually form a readable Excel workbook
    from io import BytesIO
    import pandas as pd
    workbook = BytesIO(response.content)
    # pandas should be able to read at least the summary sheet
    df = pd.read_excel(workbook, sheet_name="summary")
    assert "total_planned" in df.columns
    for f in files.values():
        f.close()
