import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import hashlib
import json
import random

st.set_page_config(page_title="Enterprise HMS", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

# =========================
# CONFIG
# =========================
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

ROLES = ["ADMIN", "HOSPITAL_MANAGER", "DOCTOR", "NURSE", "LAB_TECHNICIAN", "PHARMACIST", "ACCOUNTANT"]

COUNTRIES = ["India", "UAE", "Singapore", "Malaysia", "Kenya"]
STATES = {
    "India": ["Tamil Nadu", "Kerala", "Karnataka", "Maharashtra"],
    "UAE": ["Dubai", "Abu Dhabi"],
    "Singapore": ["Singapore"],
    "Malaysia": ["Selangor", "Penang"],
    "Kenya": ["Nairobi", "Mombasa"],
}
CITIES = {
    "Tamil Nadu": ["Salem", "Chennai", "Coimbatore", "Madurai"],
    "Kerala": ["Kochi", "Trivandrum"],
    "Karnataka": ["Bengaluru", "Mysuru"],
    "Maharashtra": ["Mumbai", "Pune"],
    "Dubai": ["Dubai"],
    "Abu Dhabi": ["Abu Dhabi"],
    "Singapore": ["Singapore"],
    "Selangor": ["Petaling Jaya"],
    "Penang": ["George Town"],
    "Nairobi": ["Nairobi"],
    "Mombasa": ["Mombasa"],
}
DEPARTMENTS = ["Cardiology", "Neurology", "Oncology", "Orthopedics", "Pediatrics", "Gynecology", "Dermatology", "ENT",
               "Ophthalmology", "Psychiatry", "Radiology", "Emergency", "ICU", "Surgery", "General Medicine",
               "Dental", "Physiotherapy", "Nutrition", "Pharmacy", "Laboratory"]
GENDERS = ["Male", "Female", "Other"]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
DISEASES = ["Diabetes", "Hypertension", "Asthma", "Cancer", "Fracture", "Migraine", "Infection", "Cardiac Disease",
            "Stroke", "Kidney Disease", "Pregnancy", "Skin Allergy", "Dental Issue", "Normal Checkup"]
PAYMENT_STATUS = ["Paid", "Pending", "Partially Paid"]
HOSPITAL_TYPES = ["General", "Specialty", "Multi-Specialty", "Teaching", "Research"]
ACCREDITATIONS = ["NABH", "JCI", "ISO", "None"]

# =========================
# HELPERS
# =========================
def hid(text):
    return hashlib.sha256(text.encode()).hexdigest()[:12]

def dated_range(days=365):
    end = pd.Timestamp.today().normalize()
    start = end - pd.Timedelta(days=days)
    return pd.date_range(start, end, freq="D")

def safe_choice(x):
    return random.choice(x)

def pct(a, b):
    return 0 if b == 0 else round((a - b) / b * 100, 2)

def generate_seed_data():
    hospitals = []
    for c in COUNTRIES:
        for s in STATES[c]:
            for city in CITIES[s]:
                for branch_no in range(1, 3):
                    name = f"{city} {branch_no} Hospital"
                    hospitals.append({
                        "hospital_id": hid(name),
                        "hospital_name": name,
                        "country": c,
                        "state": s,
                        "city": city,
                        "branch": f"Branch {branch_no}",
                        "hospital_type": safe_choice(HOSPITAL_TYPES),
                        "accreditation": safe_choice(ACCREDITATIONS),
                        "capacity": random.randint(120, 650),
                        "emergency_available": random.choice([True, True, True, False]),
                        "created_date": pd.Timestamp.today() - pd.Timedelta(days=random.randint(100, 2500)),
                    })
    hospitals = pd.DataFrame(hospitals)

    departments = []
    for _, h in hospitals.iterrows():
        for d in DEPARTMENTS:
            departments.append({
                "department_id": hid(f"{h.hospital_id}-{d}"),
                "hospital_id": h.hospital_id,
                "department_name": d,
                "head_doctor": f"Dr. {safe_choice(['Asha','Ravi','Meera','John','Sara','Karthik','Nina','Arjun'])}",
                "staff_count": random.randint(8, 60),
                "patient_capacity": random.randint(20, 150),
            })
    departments = pd.DataFrame(departments)

    doctors = []
    for _, h in hospitals.sample(min(12, len(hospitals)), random_state=SEED).iterrows():
        for _ in range(random.randint(15, 35)):
            dept = safe_choice(DEPARTMENTS)
            doctors.append({
                "doctor_id": hid(f"doc-{h.hospital_id}-{random.random()}"),
                "hospital_id": h.hospital_id,
                "name": f"Dr. {safe_choice(['Asha','Ravi','Meera','John','Sara','Karthik','Nina','Arjun','Priya','Vikram'])} {safe_choice(['Iyer','Nair','Shah','Khan','Das','Reddy','Menon','Patel'])}",
                "specialization": dept,
                "department": dept,
                "experience_years": random.randint(1, 30),
                "qualification": safe_choice(["MBBS", "MBBS, MD", "MBBS, MS", "MBBS, DNB", "MBBS, DM", "MBBS, MCh"]),
                "availability": safe_choice(["Available", "On Leave", "On Call"]),
                "hospital_branch": h["branch"],
                "rating": round(np.clip(np.random.normal(4.4, 0.35), 2.5, 5.0), 1),
            })
    doctors = pd.DataFrame(doctors)

    patients = []
    dates = dated_range(365)
    for i in range(2500):
        reg = safe_choice(dates)
        country = safe_choice(COUNTRIES)
        state = safe_choice(STATES[country])
        city = safe_choice(CITIES[state])
        patients.append({
            "patient_id": f"P{i+1:05d}",
            "full_name": f"{safe_choice(['Anu','Kavin','Priya','Rahul','Maya','Naveen','Sahana','Arun'])} {safe_choice(['Kumar','Rao','Patel','Singh','Iyer','Nair','Das','Reddy'])}",
            "age": random.randint(1, 92),
            "gender": safe_choice(GENDERS),
            "dob": reg - pd.Timedelta(days=random.randint(365*1, 365*92)),
            "blood_group": safe_choice(BLOOD_GROUPS),
            "mobile_number": f"+91-{random.randint(6000000000,9999999999)}",
            "email": f"user{i+1}@example.com",
            "address": f"{city}, {state}",
            "country": country,
            "emergency_contact": f"+91-{random.randint(6000000000,9999999999)}",
            "insurance_details": safe_choice(["None", "Star Health", "HDFC Ergo", "Bajaj Allianz", "ICICI Lombard"]),
            "registration_date": reg,
            "disease": safe_choice(DISEASES),
            "status": safe_choice(["Admitted", "Discharged", "Returning", "Under Treatment"]),
            "hospital_id": safe_choice(hospitals["hospital_id"].tolist()),
            "department": safe_choice(DEPARTMENTS),
        })
    patients = pd.DataFrame(patients)

    appts = []
    for i in range(5000):
        dt = safe_choice(dates) + pd.Timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
        appts.append({
            "appointment_id": f"A{i+1:05d}",
            "patient_id": safe_choice(patients["patient_id"].tolist()),
            "doctor_id": safe_choice(doctors["doctor_id"].tolist()),
            "hospital_id": safe_choice(hospitals["hospital_id"].tolist()),
            "department": safe_choice(DEPARTMENTS),
            "appointment_date": dt,
            "status": safe_choice(["Completed", "Cancelled", "Waiting", "No Show"]),
            "waiting_time_min": max(0, int(np.random.normal(26, 15))),
            "is_emergency": random.choice([True, False, False, False]),
        })
    appointments = pd.DataFrame(appts)

    billing = []
    for i in range(3200):
        amount = max(50, round(np.random.lognormal(mean=8.2, sigma=0.6), 2))
        billing.append({
            "invoice_id": f"INV{i+1:05d}",
            "patient_id": safe_choice(patients["patient_id"].tolist()),
            "hospital_id": safe_choice(hospitals["hospital_id"].tolist()),
            "department": safe_choice(DEPARTMENTS),
            "invoice_date": safe_choice(dates),
            "amount": amount,
            "paid_amount": round(amount * random.uniform(0.4, 1.0), 2),
            "status": safe_choice(PAYMENT_STATUS),
            "insurance_claim": random.choice([True, False, False]),
        })
    billing = pd.DataFrame(billing)

    ot = []
    for i in range(600):
        start = safe_choice(dates) + pd.Timedelta(hours=random.randint(6, 18))
        duration = random.randint(30, 420)
        ot.append({
            "surgery_id": f"S{i+1:05d}",
            "hospital_id": safe_choice(hospitals["hospital_id"].tolist()),
            "department": safe_choice(["Surgery", "Orthopedics", "Cardiology", "Neurology", "Gynecology"]),
            "surgeon": safe_choice(doctors["name"].tolist()),
            "operation_type": safe_choice(["Appendectomy", "Bypass", "Fracture Fixation", "C-section", "Neuro Procedure"]),
            "start_time": start,
            "duration_min": duration,
            "success": random.choice([True, True, True, False]),
            "equipment_usage": round(random.uniform(45, 98), 2),
        })
    ot = pd.DataFrame(ot)

    icu = []
    for i in range(700):
        vt = safe_choice(dates) + pd.Timedelta(hours=random.randint(0, 23))
        icu.append({
            "icu_record_id": f"ICU{i+1:05d}",
            "patient_id": safe_choice(patients["patient_id"].tolist()),
            "hospital_id": safe_choice(hospitals["hospital_id"].tolist()),
            "heart_rate": random.randint(50, 150),
            "blood_pressure_sys": random.randint(90, 180),
            "blood_pressure_dia": random.randint(50, 110),
            "temperature": round(np.random.normal(98.4, 1.4), 1),
            "oxygen_level": random.randint(78, 100),
            "respiration_rate": random.randint(10, 30),
            "record_time": vt,
        })
    icu = pd.DataFrame(icu)

    lab = []
    for i in range(1800):
        lab.append({
            "lab_id": f"LAB{i+1:05d}",
            "patient_id": safe_choice(patients["patient_id"].tolist()),
            "hospital_id": safe_choice(hospitals["hospital_id"].tolist()),
            "test_type": safe_choice(["Blood Test", "Urine Test", "MRI", "CT Scan", "X-Ray", "Pathology"]),
            "test_date": safe_choice(dates),
            "result": safe_choice(["Normal", "Abnormal", "Critical"]),
            "abnormal_flag": random.choice([True, False, False]),
        })
    lab = pd.DataFrame(lab)

    pharmacy = []
    medicines = ["Paracetamol", "Amoxicillin", "Metformin", "Atorvastatin", "Ibuprofen", "Omeprazole", "Amlodipine"]
    for i in range(900):
        expiry = pd.Timestamp.today() + pd.Timedelta(days=random.randint(15, 900))
        pharmacy.append({
            "medicine_id": f"M{i+1:05d}",
            "hospital_id": safe_choice(hospitals["hospital_id"].tolist()),
            "medicine_name": safe_choice(medicines),
            "stock_qty": random.randint(0, 5000),
            "consumption_qty": random.randint(0, 300),
            "expiry_date": expiry,
            "supplier": safe_choice(["ABC Pharma", "MediSupply", "Global Meds", "HealthLine"]),
        })
    pharmacy = pd.DataFrame(pharmacy)

    users = pd.DataFrame([
        {"username": "admin", "password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "ADMIN"},
        {"username": "manager", "password": hashlib.sha256("manager123".encode()).hexdigest(), "role": "HOSPITAL_MANAGER"},
        {"username": "doctor", "password": hashlib.sha256("doctor123".encode()).hexdigest(), "role": "DOCTOR"},
    ])

    return {
        "hospitals": hospitals,
        "departments": departments,
        "doctors": doctors,
        "patients": patients,
        "appointments": appointments,
        "billing": billing,
        "ot": ot,
        "icu": icu,
        "lab": lab,
        "pharmacy": pharmacy,
        "users": users,
    }

@st.cache_data
def load_data():
    return generate_seed_data()

data = load_data()

# =========================
# AUTH
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

def login_user(username, password):
    pw = hashlib.sha256(password.encode()).hexdigest()
    u = data["users"]
    row = u[(u["username"] == username) & (u["password"] == pw)]
    if len(row):
        st.session_state.logged_in = True
        st.session_state.role = row.iloc[0]["role"]
        st.session_state.username = username
        return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# =========================
# SIDEBAR LOGIN
# =========================
with st.sidebar:
    st.title("🏥 HMS Login")
    if not st.session_state.logged_in:
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="admin123")
        if st.button("Login", use_container_width=True):
            if login_user(username, password):
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        st.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()

if not st.session_state.logged_in:
    st.title("Enterprise Multi-International Hospital Management System")
    st.info("Use admin123, manager123, or doctor123 to enter the dashboard.")
    st.stop()

# =========================
# FILTERS
# =========================
hospitals = data["hospitals"]
patients = data["patients"]
doctors = data["doctors"]
appointments = data["appointments"]
billing = data["billing"]
ot = data["ot"]
icu = data["icu"]
lab = data["lab"]
pharmacy = data["pharmacy"]

with st.sidebar:
    st.subheader("Global Filters")
    hospital_sel = st.multiselect("Hospital", hospitals["hospital_name"].unique().tolist(), default=hospitals["hospital_name"].unique().tolist()[:3])
    selected_hospital_ids = hospitals[hospitals["hospital_name"].isin(hospital_sel)]["hospital_id"].tolist()
    dept_sel = st.multiselect("Department", DEPARTMENTS, default=DEPARTMENTS[:5])
    country_sel = st.multiselect("Country", COUNTRIES, default=COUNTRIES)
    gender_sel = st.multiselect("Gender", GENDERS, default=GENDERS)
    disease_sel = st.multiselect("Disease", DISEASES, default=DISEASES)
    age_min, age_max = st.slider("Age Range", 0, 100, (0, 100))
    date_min = pd.Timestamp.today().normalize() - pd.Timedelta(days=365)
    date_max = pd.Timestamp.today().normalize()
    date_range = st.date_input("Date Range", value=(date_min.date(), date_max.date()))
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

# =========================
# FILTER APPLY
# =========================
p = patients[
    patients["hospital_id"].isin(selected_hospital_ids) &
    patients["department"].isin(dept_sel) &
    patients["country"].isin(country_sel) &
    patients["gender"].isin(gender_sel) &
    patients["disease"].isin(disease_sel) &
    patients["age"].between(age_min, age_max) &
    patients["registration_date"].between(start_date, end_date)
].copy()

a = appointments[
    appointments["hospital_id"].isin(selected_hospital_ids) &
    appointments["department"].isin(dept_sel) &
    appointments["appointment_date"].dt.date.between(start_date.date(), end_date.date())
].copy()

b = billing[
    billing["hospital_id"].isin(selected_hospital_ids) &
    billing["department"].isin(dept_sel) &
    billing["invoice_date"].between(start_date, end_date)
].copy()

d = doctors[doctors["hospital_id"].isin(selected_hospital_ids)].copy()
o = ot[ot["hospital_id"].isin(selected_hospital_ids)].copy()
i = icu[icu["hospital_id"].isin(selected_hospital_ids)].copy()
l = lab[lab["hospital_id"].isin(selected_hospital_ids)].copy()
ph = pharmacy[pharmacy["hospital_id"].isin(selected_hospital_ids)].copy()

# =========================
# KPI LOGIC
# =========================
total_patients = len(p)
new_patients = len(p[p["registration_date"] >= (end_date - pd.Timedelta(days=30))])
returning_patients = len(p[p["status"] == "Returning"])
discharged_patients = len(p[p["status"] == "Discharged"])
admission_rate = round((len(p[p["status"] == "Admitted"]) / max(1, len(p))) * 100, 2)
death_rate = round(np.random.uniform(0.1, 1.2), 2)
recovery_rate = round(np.random.uniform(78, 96), 2)

total_doctors = len(d)
total_employees = total_doctors + int(len(hospitals[hospitals["hospital_name"].isin(hospital_sel)]) * 120)
revenue = round(b["paid_amount"].sum(), 2)
occupancy_rate = round(np.clip(np.random.normal(76, 9), 45, 98), 2)
patient_satisfaction = round(np.clip(np.random.normal(89, 4), 65, 99), 1)
emergency_cases = int(a["is_emergency"].sum()) if not a.empty else 0
avg_waiting = round(a["waiting_time_min"].mean(), 1) if len(a) else 0
doctor_performance = round(d["rating"].mean(), 2) if len(d) else 0
department_efficiency = round(np.clip(np.random.normal(84, 6), 60, 99), 1)

# =========================
# TITLE
# =========================
st.title("Enterprise Multi-International HMS Dashboard")
st.caption("Login → Select Hospital → Select Department → Apply Filters → View Dashboard → Analyze Graphs → Generate Text Insights → Export Reports")

# =========================
# KPI CARDS
# =========================
cols = st.columns(5)
metrics = [
    ("Total Patients", total_patients),
    ("Total Doctors", total_doctors),
    ("Revenue", f"₹ {revenue:,.2f}"),
    ("Occupancy Rate", f"{occupancy_rate}%"),
    ("Patient Satisfaction", f"{patient_satisfaction}%"),
]
for c, (label, val) in zip(cols, metrics[:5]):
    c.metric(label, val)

cols2 = st.columns(5)
metrics2 = [
    ("New Patients", new_patients),
    ("Returning Patients", returning_patients),
    ("Discharged Patients", discharged_patients),
    ("Emergency Cases", emergency_cases),
    ("Avg Waiting Time", f"{avg_waiting} min"),
]
for c, (label, val) in zip(cols2, metrics2):
    c.metric(label, val)

# =========================
# TABS
# =========================
tabs = st.tabs([
    "Executive Dashboard", "Patients", "Doctors", "Appointments",
    "EHR", "OT & ICU", "Lab & Pharmacy", "Billing", "Analytics", "Reports"
])

# ---- Dashboard ----
with tabs[0]:
    st.subheader("Hospital Performance Intelligence")
    c1, c2 = st.columns([2, 1])
    with c1:
        daily = p.groupby(p["registration_date"].dt.date).size().reset_index(name="count")
        if not daily.empty:
            fig = px.line(daily, x="registration_date", y="count", title="Daily Patient Growth Trend")
            fig.update_layout(xaxis_title="Date", yaxis_title="Patients")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Patient admission increased over the selected period based on registration trend.")
    with c2:
        rating_df = d.sort_values("rating", ascending=False).head(10)
        if not rating_df.empty:
            fig = px.bar(rating_df, x="rating", y="name", orientation="h", title="Top Doctor Ranking")
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        dept_counts = p["department"].value_counts().reset_index()
        dept_counts.columns = ["department", "count"]
        if not dept_counts.empty:
            fig = px.pie(dept_counts, values="count", names="department", title="Patient Distribution by Department")
            st.plotly_chart(fig, use_container_width=True)
    with c4:
        rev = b.groupby("department")["paid_amount"].sum().reset_index().sort_values("paid_amount", ascending=False)
        if not rev.empty:
            fig = px.bar(rev, x="department", y="paid_amount", title="Department Revenue")
            st.plotly_chart(fig, use_container_width=True)

# ---- Patients ----
with tabs[1]:
    st.subheader("Patient Management")
    st.dataframe(p.head(200), use_container_width=True, height=350)
    c1, c2, c3 = st.columns(3)
    c1.metric("Admission Rate", f"{admission_rate}%")
    c2.metric("Death Rate", f"{death_rate}%")
    c3.metric("Recovery Rate", f"{recovery_rate}%")
    monthly = p.groupby(p["registration_date"].dt.to_period("M")).size().reset_index(name="count")
    monthly["registration_date"] = monthly["registration_date"].astype(str)
    if not monthly.empty:
        fig = px.bar(monthly, x="registration_date", y="count", title="Monthly Patient Growth")
        st.plotly_chart(fig, use_container_width=True)

# ---- Doctors ----
with tabs[2]:
    st.subheader("Doctor Performance")
    perf = d[["name", "department", "experience_years", "rating", "availability"]].copy()
    if not perf.empty:
        perf["patients_treated"] = np.random.randint(80, 1800, len(perf))
        perf["success_rate"] = np.round(np.random.uniform(82, 99, len(perf)), 1)
        st.dataframe(perf.sort_values("rating", ascending=False).head(200), use_container_width=True, height=350)
        fig = px.scatter(perf, x="patients_treated", y="rating", color="department", size="experience_years",
                         title="Doctor Performance Score")
        st.plotly_chart(fig, use_container_width=True)

# ---- Appointments ----
with tabs[3]:
    st.subheader("Appointment Analytics")
    st.dataframe(a.head(200), use_container_width=True, height=300)
    if not a.empty:
        a["hour"] = a["appointment_date"].dt.hour
        heat = a.groupby(["department", "hour"]).size().reset_index(name="count")
        fig = px.density_heatmap(heat, x="hour", y="department", z="count", title="Peak Hours Heat Map")
        st.plotly_chart(fig, use_container_width=True)
    trend = a.groupby(a["appointment_date"].dt.date).size().reset_index(name="count")
    if not trend.empty:
        fig2 = px.area(trend, x="appointment_date", y="count", title="Appointment Trend")
        st.plotly_chart(fig2, use_container_width=True)

# ---- EHR ----
with tabs[4]:
    st.subheader("Electronic Health Record Analytics")
    ehr = p[["patient_id", "full_name", "disease", "age", "gender", "status", "department"]].copy()
    st.dataframe(ehr.head(200), use_container_width=True, height=300)
    freq = p["disease"].value_counts().reset_index()
    freq.columns = ["disease", "count"]
    if not freq.empty:
        fig = px.pie(freq.head(8), values="count", names="disease", title="Disease Frequency")
        st.plotly_chart(fig, use_container_width=True)
    risk = p.copy()
    if not risk.empty:
        risk["risk_score"] = np.round(np.clip((risk["age"] / 100) * 100 + np.random.normal(0, 10, len(risk)), 0, 100), 1)
        st.dataframe(risk[["patient_id", "full_name", "disease", "risk_score"]].sort_values("risk_score", ascending=False).head(100),
                     use_container_width=True, height=250)

# ---- OT & ICU ----
with tabs[5]:
    st.subheader("Operation Theatre and ICU Monitoring")
    c1, c2 = st.columns(2)
    with c1:
        st.dataframe(o.head(100), use_container_width=True, height=300)
        util = round(o["duration_min"].mean() / 420 * 100, 2) if len(o) else 0
        st.metric("OT Utilization", f"{util}%")
        if not o.empty:
            fig = px.box(o, y="duration_min", color="department", title="Surgery Duration Distribution")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.dataframe(i.head(100), use_container_width=True, height=300)
        critical = len(i[(i["oxygen_level"] < 90) | (i["heart_rate"] > 120)])
        st.metric("Critical ICU Patients", critical)
        if not i.empty:
            fig = px.scatter(i, x="oxygen_level", y="heart_rate", color="hospital_id", title="ICU Vitals Scatter")
            st.plotly_chart(fig, use_container_width=True)

# ---- Lab & Pharmacy ----
with tabs[6]:
    st.subheader("Laboratory and Pharmacy")
    c1, c2 = st.columns(2)
    with c1:
        st.dataframe(l.head(100), use_container_width=True, height=250)
        if not l.empty:
            fig = px.bar(l["test_type"].value_counts().reset_index(), x="test_type", y="count", title="Lab Test Volume")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.dataframe(ph.head(100), use_container_width=True, height=250)
        ph2 = ph.copy()
        if not ph2.empty:
            ph2["expiry_soon"] = ph2["expiry_date"] < (pd.Timestamp.today() + pd.Timedelta(days=90))
            fig = px.histogram(ph2, x="stock_qty", title="Medicine Stock Distribution")
            st.plotly_chart(fig, use_container_width=True)

# ---- Billing ----
with tabs[7]:
    st.subheader("Billing and Insurance")
    st.dataframe(b.head(200), use_container_width=True, height=320)
    monthly_income = b.groupby(b["invoice_date"].dt.to_period("M"))["paid_amount"].sum().reset_index()
    monthly_income["invoice_date"] = monthly_income["invoice_date"].astype(str)
    if not monthly_income.empty:
        fig = px.line(monthly_income, x="invoice_date", y="paid_amount", title="Monthly Income")
        st.plotly_chart(fig, use_container_width=True)
    outstanding = round((b["amount"] - b["paid_amount"]).sum(), 2) if not b.empty else 0
    st.metric("Outstanding Payments", f"₹ {outstanding:,.2f}")

# ---- Analytics ----
with tabs[8]:
    st.subheader("Advanced Data Analytics")
    st.markdown(f"""
**Descriptive:** Total patients {total_patients}, revenue ₹ {revenue:,.2f}, admissions {len(p[p["status"] == "Admitted"]) if not p.empty else 0}.

**Diagnostic:** Higher admissions are associated with emergency cases and high appointment volume in busy departments.

**Predictive:** Next month admissions are forecast to rise slightly if the current growth trend continues.

**Prescriptive:** Add staff in peak-hour departments, optimize ICU beds, and prioritize emergency queue routing.
""")
    if not p.empty:
        corr = pd.DataFrame({
            "age": p["age"].astype(float),
            "risk_proxy": np.clip(p["age"] / 100 * 80 + np.random.normal(0, 8, len(p)), 0, 100),
            "billing_proxy": np.random.uniform(1000, 50000, len(p))
        }).corr()
        fig = px.imshow(corr, text_auto=True, title="Correlation Analysis")
        st.plotly_chart(fig, use_container_width=True)

# ---- Reports ----
with tabs[9]:
    st.subheader("Report Generator")
    report_text = f"""
Hospital Performance Summary

Total Patients: {total_patients}
Total Doctors: {total_doctors}
Revenue: ₹ {revenue:,.2f}
Occupancy Rate: {occupancy_rate}%
Patient Satisfaction: {patient_satisfaction}%
Emergency Cases: {emergency_cases}
Average Waiting Time: {avg_waiting} min
Doctor Performance: {doctor_performance}
Department Efficiency: {department_efficiency}%

Summary:
Cardiology and emergency services are driving activity. Waiting time can be reduced by increasing staffing during peak hours.
"""
    st.text_area("Auto Summary", report_text, height=240)
    if not p.empty:
        csv = p.to_csv(index=False).encode("utf-8")
        st.download_button("Download Patient CSV", csv, file_name="patients_export.csv", mime="text/csv")
        json_data = p.head(100).to_json(orient="records").encode("utf-8")
        st.download_button("Download JSON", json_data, file_name="patients_export.json", mime="application/json")

# =========================
# FOOTER
# =========================
st.sidebar.markdown("---")
st.sidebar.caption("Built for Streamlit deployment with seeded demo data.")