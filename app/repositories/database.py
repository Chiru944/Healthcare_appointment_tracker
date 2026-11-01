"""SQLite persistence layer."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from app.config.settings import DATABASE_PATH

SCHEMA = '''
CREATE TABLE IF NOT EXISTS patients (
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER NOT NULL CHECK(age BETWEEN 0 AND 125),
 phone TEXT NOT NULL, email TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS doctors (
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, specialization TEXT NOT NULL,
 working_days TEXT NOT NULL DEFAULT 'Mon,Tue,Wed,Thu,Fri', start_time TEXT NOT NULL DEFAULT '09:00', end_time TEXT NOT NULL DEFAULT '17:00', active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS appointments (
 id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL REFERENCES patients(id), doctor_id INTEGER NOT NULL REFERENCES doctors(id),
 appointment_date TEXT NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Scheduled', notes TEXT DEFAULT '',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_date ON appointments(doctor_id, appointment_date, status);
'''

@contextmanager
def connect(db_path=None):
    path = db_path or DATABASE_PATH
    if path != ':memory:': Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database(db_path=None):
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        count = conn.execute('SELECT COUNT(*) FROM doctors').fetchone()[0]
        if count == 0:
            conn.executemany('INSERT INTO doctors(name,specialization,working_days,start_time,end_time) VALUES(?,?,?,?,?)', [
                ('Dr. Anita Rao','General Physician','Mon,Tue,Wed,Thu,Fri','09:00','17:00'),
                ('Dr. Kiran Mehta','Pediatrician','Mon,Tue,Wed,Thu,Fri,Sat','10:00','16:00'),
                ('Dr. Sara Thomas','Dermatologist','Tue,Wed,Thu','11:00','15:00')])
