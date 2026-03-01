# HomeCare Service Reconciliation

This repository contains a Python-based web application intended to automate the reconciliation of planned, performed, and authorized service hours for a Swiss home care (Spitex) organization. The system provides a secure, independent layer to validate and control service delivery using exported Excel files.

## Features

- Upload Excel exports containing:
  - Planned service schedules
  - Recorded and billed service hours
  - Authorized prescription volumes
- Rule-based matching of services by patient, date, and tariff category
- Identification of discrepancies (missing, extra, or mismatched services)
- Aggregation and monitoring of service volumes over configurable authorization periods
- Threshold alerts for overutilization or nearing limits
- Downloadable reports for audit and transparency

## Technology Stack

- FastAPI backend
- Pandas for data ingestion and transformation
- Python `openpyxl` for Excel handling
- In-memory processing with minimal data retention
- Option for role-based access control and secure transport

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage

Send a POST request to `/reconcile` with three Excel files (as form-data):
- `plan_file`
- `actual_file`
- `prescription_file`

The API will return a reconciliation report in JSON and optionally as an Excel download.

## Security & Compliance

- All processing is done in memory; files are not stored permanently.
- HTTPS and authentication should be configured when deploying in a Swiss-compliant hosting environment.
- Role-based access dependencies can be expanded in `app/main.py`.

## License

MIT License (placeholder).