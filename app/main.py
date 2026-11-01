"""Streamlit UI for the Healthcare Appointment Tracker.

Use synthetic/demo patient data only. This application is not intended for real
patient records or clinical decision-making.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

# Make imports work when launched with: python -m streamlit run app/main.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.config.settings import CLINIC_CLOSE, CLINIC_OPEN
from app.repositories.database import initialize_database
from app.services.appointment_service import AppointmentService, ValidationError

load_dotenv(PROJECT_ROOT / ".env")
st.set_page_config(
    page_title="Healthcare Appointment Tracker",
    page_icon="🩺",
    layout="wide",
)

initialize_database()
service = AppointmentService(clinic_open=CLINIC_OPEN, clinic_close=CLINIC_CLOSE)

# Header styling and top navigation. The selected page is stored in session state
# so clicking a header button changes the view without a sidebar menu.
st.markdown(
    """
    <style>
    :root {
      --color-primary: #1e3a8a;
      --color-primary-light: #eff6ff;
      --color-success: #065f46;
      --color-success-light: #ecfdf5;
      --color-bg-main: #f8fafc;
      --color-bg-card: #ffffff;
      --color-text-main: #0f172a;
      --color-text-muted: #475569;
      --color-border: #e2e8f0;
      --color-lock-icon: #d97706;
    }

    .stApp { background: var(--color-bg-main); color: var(--color-text-main); }
    .block-container { padding-top: 1.1rem; padding-bottom: 2.2rem; max-width: 1500px; }
    [data-testid="stHeader"] { background: rgba(248,250,252,.96); }
    .hat-brand { display:flex; align-items:center; gap:14px; margin:0 0 8px 0; }
    .hat-logo { display:flex; align-items:center; justify-content:center; width:54px; height:54px;
        flex-shrink:0; border-radius:16px; background:var(--color-primary); color:white;
        font-size:28px; box-shadow:0 6px 16px rgba(30,58,138,.16); }
    .hat-title { font-size:clamp(1.45rem,2.8vw,2.15rem); line-height:1.15; font-weight:800;
        color:var(--color-primary); margin:0; }
    .hat-subtitle { font-size:.95rem; color:var(--color-text-muted); margin:4px 0 12px 0; }

    /* Horizontal header navigation buttons */
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {
        min-height:46px; width:100%; border-radius:11px; font-weight:700;
        border:1px solid var(--color-border); color:var(--color-primary);
        background:var(--color-bg-card); box-shadow:0 2px 5px rgba(15,23,42,.04);
        transition:background .15s ease, border-color .15s ease, transform .15s ease;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:hover {
        background:var(--color-primary-light); border-color:var(--color-primary);
        color:var(--color-primary); transform:translateY(-1px);
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button[kind="primary"] {
        background:var(--color-primary); border:1px solid var(--color-primary); color:#fff;
        box-shadow:0 4px 10px rgba(30,58,138,.18);
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button[kind="primary"]:hover {
        background:var(--color-success); border-color:var(--color-success); color:#fff;
    }
    .hat-divider { height:2px; background:var(--color-border); margin:10px 0 24px 0; border:0; }

    h1, h2, h3, h4 { color:var(--color-primary); }
    [data-testid="stMetric"] { background:var(--color-bg-card); border:1px solid var(--color-border);
        padding:16px 18px; border-radius:14px; box-shadow:0 2px 7px rgba(15,23,42,.035); }
    [data-testid="stForm"] { background:var(--color-bg-card); border:1px solid var(--color-border);
        border-radius:14px; padding:18px; }
    div[data-testid="stAlert"] { border-radius:10px; }
    div[data-testid="stDataFrame"] { border:1px solid var(--color-border); border-radius:12px; overflow:hidden; }
    button[kind="secondaryFormSubmit"], button[kind="primaryFormSubmit"] {
        border-radius:10px; font-weight:700;
    }
    a { color:var(--color-primary); }
    @media (max-width: 800px) {
        .hat-subtitle { font-size:.85rem; }
        .block-container { padding-left:1rem; padding-right:1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
import streamlit as st

st.markdown(
    """
    <style>
    /* ========================================
       HEALTHCARE APPOINTMENT TRACKER
       PROFESSIONAL DARK THEME
       ======================================== */

    :root {
        --color-primary: #10B981;
        --color-primary-hover: #059669;
        --color-primary-light: #064E3B;

        --color-bg-main: #0B1120;
        --color-bg-card: #151F32;
        --color-bg-hover: #1E293B;
        --color-bg-input: #111827;

        --color-text-main: #F1F5F9;
        --color-text-muted: #94A3B8;

        --color-border: #293548;
        --color-success: #34D399;
        --color-warning: #FBBF24;
        --color-danger: #FB7185;
        --color-info: #60A5FA;

        --radius-card: 16px;
        --radius-input: 10px;

        --shadow-card:
            0 8px 24px rgba(0, 0, 0, 0.20);
    }

    /* Main application background */

    .stApp {
        background:
            radial-gradient(
                ellipse at top left,
                rgba(16, 185, 129, 0.07),
                transparent 35%
            ),
            var(--color-bg-main);

        color: var(--color-text-main);
        font-family: Inter, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Main headings */

    h1 {
        color: var(--color-text-main) !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    h2 {
        color: var(--color-text-main) !important;
        font-weight: 700 !important;
    }

    h3 {
        color: #D1FAE5 !important;
        font-weight: 650 !important;
    }

    p, label, li {
        color: #CBD5E1;
    }

    /* Horizontal rule */

    hr {
        border-color: var(--color-border) !important;
        margin: 1.5rem 0 !important;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background: #101827;
        border-right: 1px solid var(--color-border);
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #F1F5F9 !important;
    }

    /* Buttons */

    .stButton > button,
    .stDownloadButton > button,
    button[kind="primary"] {
        background: linear-gradient(
            135deg,
            #10B981,
            #059669
        );

        color: #FFFFFF !important;
        border: 1px solid rgba(52, 211, 153, 0.35);
        border-radius: 10px;

        padding: 0.65rem 1.25rem;
        min-height: 42px;

        font-weight: 650;
        letter-spacing: 0.2px;

        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.12);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: linear-gradient(
            135deg,
            #059669,
            #047857
        );

        border-color: #34D399;
        transform: translateY(-2px);

        box-shadow: 0 7px 18px rgba(16, 185, 129, 0.22);
    }

    .stButton > button:focus,
    .stDownloadButton > button:focus {
        outline: 2px solid #34D399 !important;
        outline-offset: 3px;
    }

    /* Text inputs and text areas */

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTimeInput input,
    .stTextArea textarea {
        background-color: var(--color-bg-input) !important;
        color: var(--color-text-main) !important;

        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-input) !important;

        padding: 0.7rem 0.85rem;
        transition: border-color 0.2s ease,
                    box-shadow 0.2s ease;
    }

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus,
    .stTimeInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--color-primary) !important;

        box-shadow:
            0 0 0 3px rgba(16, 185, 129, 0.15) !important;
    }

    /* Select boxes */

    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        background-color: var(--color-bg-input) !important;
        color: var(--color-text-main) !important;

        border-radius: var(--radius-input) !important;
        border-color: var(--color-border) !important;
    }

    /* Dropdown options */

    [role="listbox"],
    [role="option"] {
        background-color: #151F32 !important;
        color: #E5E7EB !important;
    }

    [role="option"]:hover {
        background-color: #1E293B !important;
    }

    /* Metric cards */

    [data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            #182438,
            #111A2B
        );

        border: 1px solid var(--color-border);
        border-radius: var(--radius-card);

        padding: 1.25rem 1.35rem;

        box-shadow: var(--shadow-card);

        transition: transform 0.2s ease,
                    border-color 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(16, 185, 129, 0.55);
    }

    [data-testid="stMetricLabel"] {
        color: var(--color-text-muted) !important;
        font-size: 0.9rem !important;
        font-weight: 550 !important;
    }

    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricDelta"] {
        color: var(--color-success) !important;
    }

    /* Dataframes and tables */

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--color-border);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Tabs */

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid var(--color-border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--color-text-muted);

        border-radius: 9px 9px 0 0;
        padding: 0.7rem 1rem;
    }

    .stTabs [aria-selected="true"] {
        color: #34D399 !important;
        border-bottom: 2px solid #10B981 !important;
        font-weight: 700;
    }

    /* Expanders */

    [data-testid="stExpander"] {
        background: var(--color-bg-card);
        border: 1px solid var(--color-border);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Success, error, warning and info messages */

    [data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid var(--color-border);
    }

    /* Form containers */

    [data-testid="stForm"] {
        background: var(--color-bg-card);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-card);

        padding: 1.5rem;
        box-shadow: var(--shadow-card);
    }

    /* Horizontal navigation buttons */

    div[data-testid="stHorizontalBlock"] .stButton > button {
        width: 100%;
        min-height: 46px;
        border-radius: 10px;
    }

    /* Links */

    a {
        color: #6EE7B7 !important;
        text-decoration: none;
    }

    a:hover {
        color: #A7F3D0 !important;
        text-decoration: underline;
    }

    /* Dividers and captions */

    [data-testid="stCaptionContainer"] {
        color: var(--color-text-muted) !important;
    }

    /* Scrollbar */

    ::-webkit-scrollbar {
        width: 9px;
        height: 9px;
    }

    ::-webkit-scrollbar-track {
        background: #0B1120;
    }

    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #10B981;
    }

    /* Mobile-friendly spacing */

    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.8rem 2rem;
        }

        h1 {
            font-size: 1.8rem !important;
        }

        [data-testid="stMetric"] {
            padding: 0.9rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hat-brand"><div class="hat-logo">🩺</div>'
    '<div><div class="hat-title">Healthcare Appointment Tracker</div>'
    '<div class="hat-subtitle">Simple, organized clinic scheduling</div></div></div>',
    unsafe_allow_html=True,
)
st.caption(
    "Demo mode • Use synthetic patient data only. Do not enter real patient or health information."
)

pages = [
    "Dashboard",
    "Patients",
    "Doctors",
    "Appointments",
    "Daily Schedule",
    "Reports",
]
if "active_page" not in st.session_state or st.session_state.active_page not in pages:
    st.session_state.active_page = "Dashboard"

nav_columns = st.columns(len(pages), gap="small")
for nav_column, nav_page in zip(nav_columns, pages):
    with nav_column:
        if st.button(
            nav_page,
            key=f"header_nav_{nav_page.lower().replace(' ', '_')}",
            type="primary" if st.session_state.active_page == nav_page else "secondary",
            width="stretch",
        ):
            st.session_state.active_page = nav_page
            st.rerun()

st.markdown('<hr class="hat-divider">', unsafe_allow_html=True)
page = st.session_state.active_page


def show_table(
    rows: list[dict], empty_message: str, *, columns: list[str] | None = None
) -> None:
    """Render a table or a friendly empty-state message."""
    if rows:
        frame = pd.DataFrame(rows)
        if columns:
            frame = frame.reindex(columns=columns)
        st.dataframe(frame, width="stretch", hide_index=True)
    else:
        st.info(empty_message)


def notify(action) -> None:
    """Run a write action and display user-friendly validation errors."""
    try:
        action()
        st.success("Saved successfully.")
    except (ValidationError, ValueError, TypeError) as exc:
        st.error(str(exc))
    except Exception:
        st.error("Something went wrong while saving. Please try again.")
        st.exception(Exception("Unexpected error. Check the terminal for details."))


try:
    patients = service.list_patients()
    doctors = service.list_doctors()
except Exception as exc:
    st.error(
        "The database could not be loaded. Stop the app and restart it. If the problem continues, share the terminal error."
    )
    st.exception(exc)
    st.stop()

if page == "Dashboard":
    today = date.today().isoformat()
    all_appointments = service.list_appointments()
    today_appointments = [
        item for item in all_appointments if item["appointment_date"] == today
    ]
    upcoming = [
        item
        for item in all_appointments
        if today
        <= item["appointment_date"]
        <= (date.today() + timedelta(days=7)).isoformat()
        and item["status"] == "Scheduled"
    ]

    metrics = st.columns(4)
    metrics[0].metric("Patients", len(patients))
    metrics[1].metric("Active doctors", len(doctors))
    metrics[2].metric("Today's appointments", len(today_appointments))
    metrics[3].metric("Upcoming (7 days)", len(upcoming))

    st.subheader("Today's appointments")
    show_table(today_appointments, "No appointments scheduled for today.")

    st.subheader("Upcoming reminders (next 7 days)")
    reminder_columns = [
        "appointment_date",
        "start_time",
        "patient_name",
        "doctor_name",
        "patient_phone",
        "status",
    ]
    show_table(
        upcoming,
        "No upcoming appointments in the next 7 days.",
        columns=reminder_columns,
    )

elif page == "Patients":
    st.subheader("Register patient")
    with st.form("patient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full name *", max_chars=100)
        age = col2.number_input("Age *", min_value=0, max_value=125, value=25, step=1)
        phone = col1.text_input("Phone *", max_chars=30)
        email = col2.text_input("Email (optional)", max_chars=150)
        submitted = st.form_submit_button("Register patient")
        if submitted:
            try:
                patient_id = service.add_patient(name, age, phone, email)
                st.success(f"Patient registered successfully (ID {patient_id}).")
                st.rerun()
            except (ValidationError, ValueError, TypeError) as exc:
                st.error(str(exc))

    st.subheader("Registered patients")
    show_table(service.list_patients(), "No patients registered yet.")

elif page == "Doctors":
    st.subheader("Add doctor")
    with st.form("doctor_form", clear_on_submit=True):
        name = st.text_input("Doctor name *", max_chars=100)
        specialization = st.text_input("Specialization *", max_chars=100)
        working_days = st.multiselect(
            "Working days",
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            default=["Mon", "Tue", "Wed", "Thu", "Fri"],
        )
        col1, col2 = st.columns(2)
        start_time = col1.time_input("Starts at", value=time(9, 0)).strftime("%H:%M")
        end_time = col2.time_input("Ends at", value=time(17, 0)).strftime("%H:%M")
        submitted = st.form_submit_button("Add doctor")
        if submitted:
            try:
                doctor_id = service.add_doctor(
                    name, specialization, working_days, start_time, end_time
                )
                st.success(f"Doctor added successfully (ID {doctor_id}).")
                st.rerun()
            except (ValidationError, ValueError, TypeError) as exc:
                st.error(str(exc))

    st.subheader("Doctor directory")
    show_table(
        service.list_doctors(active_only=False), "No doctors are registered yet."
    )

elif page == "Appointments":
    st.subheader("Book appointment")
    if not patients:
        st.warning("Register at least one patient before booking an appointment.")
    elif not doctors:
        st.warning(
            "No active doctors are available. Add or activate a doctor before booking."
        )
    else:
        with st.form("booking_form", clear_on_submit=True):
            patient_map = {
                f"{patient['name']} (ID {patient['id']})": patient["id"]
                for patient in patients
            }
            doctor_map = {
                f"{doctor['name']} — {doctor['specialization']} (ID {doctor['id']})": doctor[
                    "id"
                ]
                for doctor in doctors
            }
            col1, col2 = st.columns(2)
            patient_label = col1.selectbox("Patient", list(patient_map))
            doctor_label = col2.selectbox("Doctor", list(doctor_map))
            appointment_day = st.date_input(
                "Date", value=date.today(), min_value=date.today()
            )
            col1, col2 = st.columns(2)
            start_time = col1.time_input("Start time", value=time(10, 0)).strftime(
                "%H:%M"
            )
            end_time = col2.time_input("End time", value=time(10, 30)).strftime("%H:%M")
            notes = st.text_area(
                "Notes (do not include sensitive health details)", max_chars=500
            )
            submitted = st.form_submit_button("Book appointment")
            if submitted:
                try:
                    appointment_id = service.book(
                        patient_map[patient_label],
                        doctor_map[doctor_label],
                        appointment_day.isoformat(),
                        start_time,
                        end_time,
                        notes,
                    )
                    st.success(
                        f"Appointment booked successfully (ID {appointment_id})."
                    )
                    st.rerun()
                except (ValidationError, ValueError, TypeError) as exc:
                    st.error(str(exc))

    st.subheader("Manage appointments")
    all_appointments = service.list_appointments()
    show_table(all_appointments, "No appointments yet.")

    if all_appointments:
        appointment_map = {
            f"#{item['id']} {item['appointment_date']} {item['start_time']} — "
            f"{item['patient_name']} / {item['doctor_name']} [{item['status']}]": item
            for item in all_appointments
        }
        selected_label = st.selectbox(
            "Select appointment to update", list(appointment_map)
        )
        selected = appointment_map[selected_label]

        col1, col2 = st.columns(2)
        with col1:
            statuses = ["Scheduled", "Completed", "Cancelled", "No-Show"]
            new_status = st.selectbox(
                "Set status",
                statuses,
                index=statuses.index(selected["status"]),
                key="appointment_status",
            )
            if st.button("Update status"):
                try:
                    service.set_status(selected["id"], new_status)
                    st.success("Appointment status updated.")
                    st.rerun()
                except (ValidationError, ValueError, TypeError) as exc:
                    st.error(str(exc))

        with col2:
            with st.expander("Reschedule appointment"):
                new_day = st.date_input(
                    "New date",
                    value=max(
                        date.today(), date.fromisoformat(selected["appointment_date"])
                    ),
                    min_value=date.today(),
                    key="reschedule_day",
                )
                new_start = st.time_input(
                    "New start",
                    value=datetime.strptime(selected["start_time"], "%H:%M").time(),
                    key="reschedule_start",
                ).strftime("%H:%M")
                new_end = st.time_input(
                    "New end",
                    value=datetime.strptime(selected["end_time"], "%H:%M").time(),
                    key="reschedule_end",
                ).strftime("%H:%M")
                if st.button("Save reschedule"):
                    try:
                        service.reschedule(
                            selected["id"],
                            selected["patient_id"],
                            selected["doctor_id"],
                            new_day.isoformat(),
                            new_start,
                            new_end,
                            selected.get("notes", ""),
                        )
                        st.success("Appointment rescheduled successfully.")
                        st.rerun()
                    except (ValidationError, ValueError, TypeError) as exc:
                        st.error(str(exc))

elif page == "Daily Schedule":
    selected_day = st.date_input(
        "Schedule date", value=date.today(), key="schedule_day"
    )
    doctor_options = {"All doctors": None}
    doctor_options.update(
        {
            f"{doctor['name']} — {doctor['specialization']}": doctor["id"]
            for doctor in doctors
        }
    )
    selected_doctor = st.selectbox(
        "Doctor", list(doctor_options), key="schedule_doctor"
    )
    schedule = service.list_appointments(
        selected_day.isoformat(), doctor_options[selected_doctor]
    )
    st.subheader(f"Schedule for {selected_day.strftime('%d %B %Y')}")
    show_table(schedule, "No appointments for the selected date and doctor.")

elif page == "Reports":
    col1, col2, col3 = st.columns(3)
    report_start = col1.date_input(
        "From", value=date.today() - timedelta(days=30), key="report_start"
    )
    report_end = col2.date_input("To", value=date.today(), key="report_end")
    status = col3.selectbox(
        "Status", ["All", "Scheduled", "Completed", "Cancelled", "No-Show"]
    )
    search = st.text_input("Search patient, doctor, or appointment ID")

    if report_start > report_end:
        st.error("The start date must be on or before the end date.")
    else:
        filtered = [
            item
            for item in service.list_appointments(status=status, search=search)
            if report_start.isoformat()
            <= item["appointment_date"]
            <= report_end.isoformat()
        ]
        frame = pd.DataFrame(filtered)
        st.metric("Matching appointments", len(frame))
        if not frame.empty:
            st.dataframe(frame, width="stretch", hide_index=True)
            st.download_button(
                "Download CSV report",
                data=frame.to_csv(index=False).encode("utf-8"),
                file_name=f"appointments_{report_start}_{report_end}.csv",
                mime="text/csv",
            )
        else:
            st.info("No records match those filters.")
