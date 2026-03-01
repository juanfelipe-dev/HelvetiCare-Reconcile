from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from .services import reconcile_files
from .schemas import ReconciliationResult

app = FastAPI(title="HomeCare Reconciliation API",
              description="Automated service reconciliation for Swiss home care organizations",
              version="0.1.0")

# static files & templates
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# TODO: implement real authentication and role-based access control

def get_current_user():
    # placeholder dependency
    return {"username": "testuser", "roles": ["controller"]}

@app.post("/reconcile")
async def reconcile(plan_file: UploadFile = File(...),
                    actual_file: UploadFile = File(...),
                    prescription_file: UploadFile = File(...),
                    download: bool = False,
                    user: dict = Depends(get_current_user)):
    """Upload three Excel files and perform reconciliation.
    The files should be exported from the planning, billing and prescription systems.

    If `download` is true, an Excel workbook containing the report will be returned
    as a streaming download. Otherwise a JSON payload matching :class:`ReconciliationResult`
    is returned.
    """
    try:
        result = await reconcile_files(plan_file, actual_file, prescription_file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if download:
        from .utils import result_to_excel
        excel_bytes = result_to_excel(result)
        headers = {"Content-Disposition": "attachment; filename=report.xlsx"}
        return StreamingResponse(excel_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)

    # when not downloading, return JSON
    return result

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    """Serve the upload form for reconciliation."""
    return templates.TemplateResponse("index.html", {"request": request})
