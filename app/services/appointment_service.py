"""Business rules for patients, doctors, and appointments."""
from datetime import date, datetime, time
from app.repositories.database import connect

ACTIVE_STATUSES = ('Scheduled', 'Completed', 'No-Show')

class ValidationError(ValueError):
    """Raised when submitted data violates clinic rules."""

class AppointmentService:
    def __init__(self, db_path=None, clinic_open='09:00', clinic_close='17:00'):
        self.db_path, self.clinic_open, self.clinic_close = db_path, clinic_open, clinic_close

    def add_patient(self, name, age, phone, email=''):
        name, phone = name.strip(), phone.strip()
        if not name or not phone: raise ValidationError('Patient name and phone are required.')
        try: age = int(age)
        except (TypeError, ValueError): raise ValidationError('Age must be a whole number.')
        if not 0 <= age <= 125: raise ValidationError('Age must be between 0 and 125.')
        with connect(self.db_path) as c:
            cur = c.execute('INSERT INTO patients(name,age,phone,email) VALUES(?,?,?,?)', (name, age, phone, email.strip()))
            return cur.lastrowid

    def add_doctor(self, name, specialization, working_days, start_time, end_time):
        if not name.strip() or not specialization.strip():
            raise ValidationError('Doctor name and specialization are required.')
        if not working_days:
            raise ValidationError('Select at least one working day for the doctor.')
        self._parse_time(start_time)
        self._parse_time(end_time)
        if start_time >= end_time: raise ValidationError('Doctor end time must be after start time.')
        with connect(self.db_path) as c:
            cur = c.execute('INSERT INTO doctors(name,specialization,working_days,start_time,end_time) VALUES(?,?,?,?,?)',
                            (name.strip(), specialization.strip(), ','.join(working_days), start_time, end_time))
            return cur.lastrowid

    @staticmethod
    def _parse_time(value):
        try: return datetime.strptime(value, '%H:%M').time()
        except (ValueError, TypeError): raise ValidationError('Time must use HH:MM format.')

    def book(self, patient_id, doctor_id, appointment_date, start_time, end_time, notes=''):
        return self._save_appointment(None, patient_id, doctor_id, appointment_date, start_time, end_time, notes)

    def reschedule(self, appointment_id, patient_id, doctor_id, appointment_date, start_time, end_time, notes=''):
        return self._save_appointment(appointment_id, patient_id, doctor_id, appointment_date, start_time, end_time, notes)

    def _save_appointment(self, appointment_id, patient_id, doctor_id, day, start, end, notes):
        try:
            day_obj = date.fromisoformat(str(day)); start_obj = self._parse_time(start); end_obj = self._parse_time(end)
            patient_id, doctor_id = int(patient_id), int(doctor_id)
        except (ValueError, TypeError): raise ValidationError('Please provide valid patient, doctor, date, and times.')
        if day_obj < date.today(): raise ValidationError('Appointments cannot be booked in the past.')
        if start_obj >= end_obj: raise ValidationError('End time must be after start time.')
        with connect(self.db_path) as c:
            patient = c.execute('SELECT id FROM patients WHERE id=?', (patient_id,)).fetchone()
            doctor = c.execute('SELECT * FROM doctors WHERE id=? AND active=1', (doctor_id,)).fetchone()
            if not patient: raise ValidationError('Selected patient does not exist.')
            if not doctor: raise ValidationError('Selected doctor does not exist or is inactive.')
            day_name = day_obj.strftime('%a')
            if day_name not in doctor['working_days'].split(','): raise ValidationError('Doctor is not available on that day.')
            if start < doctor['start_time'] or end > doctor['end_time']: raise ValidationError('Appointment is outside doctor working hours.')
            if start < self.clinic_open or end > self.clinic_close: raise ValidationError('Appointment is outside clinic working hours.')
            if appointment_id is not None:
                existing = c.execute(
                    'SELECT status FROM appointments WHERE id=?', (int(appointment_id),)
                ).fetchone()
                if not existing:
                    raise ValidationError('Appointment not found.')
                if existing['status'] == 'Cancelled':
                    raise ValidationError('A cancelled appointment cannot be rescheduled.')

            params = [doctor_id, str(day), end, start]
            sql = "SELECT id FROM appointments WHERE doctor_id=? AND appointment_date=? AND status!='Cancelled' AND start_time < ? AND end_time > ?"
            if appointment_id is not None:
                sql += ' AND id != ?'
                params.append(int(appointment_id))
            if c.execute(sql, params).fetchone():
                raise ValidationError('This appointment overlaps another appointment for the doctor.')

            if appointment_id is None:
                cur = c.execute(
                    'INSERT INTO appointments(patient_id,doctor_id,appointment_date,start_time,end_time,notes,status) VALUES(?,?,?,?,?,?,?)',
                    (patient_id, doctor_id, str(day), start, end, notes.strip(), 'Scheduled'),
                )
                return cur.lastrowid

            c.execute(
                'UPDATE appointments SET patient_id=?,doctor_id=?,appointment_date=?,start_time=?,end_time=?,notes=? WHERE id=?',
                (patient_id, doctor_id, str(day), start, end, notes.strip(), int(appointment_id)),
            )
            return int(appointment_id)

    def set_status(self, appointment_id, status):
        if status not in ('Scheduled','Completed','Cancelled','No-Show'): raise ValidationError('Invalid appointment status.')
        with connect(self.db_path) as c:
            cur = c.execute('UPDATE appointments SET status=? WHERE id=?', (status, int(appointment_id)))
            if not cur.rowcount: raise ValidationError('Appointment not found.')

    def list_patients(self):
        with connect(self.db_path) as c: return [dict(r) for r in c.execute('SELECT * FROM patients ORDER BY name')]
    def list_doctors(self, active_only=True):
        with connect(self.db_path) as c:
            q = 'SELECT * FROM doctors' + (' WHERE active=1' if active_only else '') + ' ORDER BY name'
            return [dict(r) for r in c.execute(q)]
    def list_appointments(self, day=None, doctor_id=None, status=None, search=''):
        sql = '''SELECT a.*, p.name patient_name, p.phone patient_phone, d.name doctor_name, d.specialization
                 FROM appointments a JOIN patients p ON p.id=a.patient_id JOIN doctors d ON d.id=a.doctor_id WHERE 1=1'''
        args=[]
        if day: sql += ' AND a.appointment_date=?'; args.append(str(day))
        if doctor_id: sql += ' AND a.doctor_id=?'; args.append(int(doctor_id))
        if status and status != 'All': sql += ' AND a.status=?'; args.append(status)
        if search.strip(): sql += ' AND (p.name LIKE ? OR d.name LIKE ? OR CAST(a.id AS TEXT) LIKE ?)'; args += [f'%{search.strip()}%']*3
        sql += ' ORDER BY a.appointment_date, a.start_time'
        with connect(self.db_path) as c: return [dict(r) for r in c.execute(sql,args)]
