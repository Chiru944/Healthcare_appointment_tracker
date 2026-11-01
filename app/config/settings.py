"""Application settings."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = os.getenv("HEALTHCARE_DB_PATH", str(BASE_DIR / "healthcare.db"))
CLINIC_OPEN = os.getenv("CLINIC_OPEN", "09:00")
CLINIC_CLOSE = os.getenv("CLINIC_CLOSE", "17:00")
APPOINTMENT_MINUTES = int(os.getenv("APPOINTMENT_MINUTES", "30"))
