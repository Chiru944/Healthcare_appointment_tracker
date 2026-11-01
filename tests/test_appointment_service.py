from datetime import date, timedelta
import pytest
from app.repositories.database import initialize_database
from app.services.appointment_service import AppointmentService, ValidationError

@pytest.fixture
def service(tmp_path):
    path=str(tmp_path/'test.db'); initialize_database(path); s=AppointmentService(db_path=path)
    s.add_patient('Test Patient',30,'9000000000')
    return s

def test_successful_booking(service):
    tomorrow=(date.today()+timedelta(days=1)).isoformat()
    aid=service.book(1,1,tomorrow,'10:00','10:30')
    assert aid and service.list_appointments(day=tomorrow)[0]['status']=='Scheduled'

def test_overlapping_booking_rejected(service):
    tomorrow=(date.today()+timedelta(days=1)).isoformat()
    service.book(1,1,tomorrow,'10:00','10:30')
    with pytest.raises(ValidationError,match='overlaps'):
        service.book(1,1,tomorrow,'10:15','10:45')

def test_back_to_back_allowed(service):
    tomorrow=(date.today()+timedelta(days=1)).isoformat()
    service.book(1,1,tomorrow,'10:00','10:30')
    assert service.book(1,1,tomorrow,'10:30','11:00')

def test_past_booking_rejected(service):
    yesterday=(date.today()-timedelta(days=1)).isoformat()
    with pytest.raises(ValidationError,match='past'):
        service.book(1,1,yesterday,'10:00','10:30')

def test_cancelled_slot_can_be_rebooked(service):
    tomorrow=(date.today()+timedelta(days=1)).isoformat()
    aid=service.book(1,1,tomorrow,'10:00','10:30'); service.set_status(aid,'Cancelled')
    assert service.book(1,1,tomorrow,'10:00','10:30')

def test_invalid_patient_rejected(service):
    tomorrow=(date.today()+timedelta(days=1)).isoformat()
    with pytest.raises(ValidationError,match='patient'):
        service.book(999,1,tomorrow,'10:00','10:30')
