# Healthcare Appointment Tracker

A Streamlit + Python + SQLite clinic scheduling demo based on the supplied trainer handbook. Features include patient registration, doctor management and availability, appointment booking/rescheduling/cancellation, overlap prevention, status tracking, daily schedules, upcoming reminders, search/filter, and CSV reports.

> **Privacy:** use synthetic/demo data only. This starter application is not certified or configured for real patient records and is not, by itself, compliant with healthcare privacy regulations. Do not enter real patient data.

## Requirements
- Python 3.10+
- Windows, macOS, or Linux

## Install and run

### Windows (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app/main.py
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/main.py
```

The browser opens the local app. The SQLite database is created automatically and a few sample doctors are seeded. Patient records are not seeded. Use only fake/demo details.

## Configuration
Optional `.env` values are documented in `.env.example`. Export them in your shell or load them with your preferred environment loader. `HEALTHCARE_DB_PATH` sets the database path; `CLINIC_OPEN` and `CLINIC_CLOSE` set clinic-wide working hours. `.env` and database files are excluded from Git.

## Tests
```bash
pytest -q
```
Tests use temporary SQLite files and synthetic data. For a fully deterministic CI environment, run tests with a fixed system date or inject a clock into the service before extending the project.

## Architecture
- `app/main.py`: Streamlit presentation layer
- `app/config/settings.py`: environment-backed configuration
- `app/repositories/database.py`: SQLite schema, connection management, seed doctors
- `app/services/appointment_service.py`: validation and appointment business rules
- `app/utils/validators.py`: reusable validation helper
- `tests/`: pytest business-rule tests

## Business rules
- Rejects appointments in the past.
- Rejects overlapping active appointments for the same doctor; back-to-back appointments are allowed.
- Cancelled appointments do not block the time slot.
- Enforces doctor working days/hours and clinic-wide hours.
- Uses parameterized SQL queries and validates required values.

## Git quick start
```bash
git init
git add .
git commit -m "feat: initial healthcare appointment tracker"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

## Production-readiness gaps
Before real deployment, add authentication and role-based authorization, encrypted storage and backups, audit trails, retention/deletion workflows, secure hosting, stronger validation, monitoring, concurrency-safe transaction handling, privacy/legal review, and formal security testing. Never log patient-identifying details. Reminder display in this demo is in-app only; no SMS/email is sent.

## Header navigation

The app uses colored navigation buttons across the page header for Dashboard, Patients,
Doctors, Appointments, Daily Schedule, and Reports. Start it from the project root with:

```powershell
python -m streamlit run app/main.py
```

Do not run `python app/main.py` directly; launch Streamlit using the command above.
