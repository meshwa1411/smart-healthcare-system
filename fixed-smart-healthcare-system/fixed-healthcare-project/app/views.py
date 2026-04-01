from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from .models import Doctor, Appointment, Patient, UserProfile, MedicalReport, PatientHealthData, MedicineReminder
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def home(request):
    return render(request, 'patient/home.html')


def login_page(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # BUG FIX: use get_or_create to avoid crash if profile missing
            profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': 'patient'})
            if profile.role == "patient":
                return redirect("patient_home")
            elif profile.role == "doctor":
                return redirect("doctor_appointments")
            elif profile.role == "lab":
                return redirect("lab_dashboard")
            elif profile.role == "admin":
                return redirect("admin_dashboard")
            else:
                return redirect("patient_home")
        else:
            return render(request, "login.html", {"error": "Invalid Credentials"})
    return render(request, "login.html")


def register_page(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, "register.html")

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, role=role)

        if role == "patient":
            Patient.objects.create(user=user)
        if role == "doctor":
            Doctor.objects.create(
                name=user.username,
                specialization="General",
                experience=1,
                hospital="Not Assigned",
                available_days="Mon-Fri",
                available_time="10AM-2PM"
            )

        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "register.html")


def dashboard_redirect(request):
    if request.user.groups.filter(name='Patient').exists():
        return redirect('patient_dashboard')
    elif request.user.groups.filter(name='Doctor').exists():
        return redirect('doctor_dashboard')
    elif request.user.groups.filter(name='LabStaff').exists():
        return redirect('lab_dashboard')
    else:
        return redirect('home')


# ===============================
# DOCTOR VIEWS
# ===============================

@login_required
def doctor_dashboard(request):
    # BUG FIX: Appointment.doctor is a Doctor FK (not User FK), must fetch Doctor first
    try:
        doctor = Doctor.objects.get(name=request.user.username)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('login')

    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')
    status = {
        'pending': appointments.filter(status='Pending').count(),
        'confirmed': appointments.filter(status='Confirmed').count(),
        'rejected': appointments.filter(status='Rejected').count(),
        'total_patients': appointments.values('patient').distinct().count()
    }
    return render(request, 'doctor/doctor_dashboard.html', {
        'appointments': appointments,
        'status': status,
        'doctor': doctor
    })


@login_required
def doctor_appointments(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.role != 'doctor':
        messages.error(request, "Access denied. Doctors only.")
        return redirect('patient_home')

    try:
        doctor = Doctor.objects.get(name=request.user.username)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('home')

    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')
    pending_count = appointments.filter(status='Pending').count()
    confirmed_count = appointments.filter(status='Confirmed').count()
    rejected_count = appointments.filter(status='Rejected').count()
    total_patients = Patient.objects.count()

    return render(request, "doctor/doctor_dashboard.html", {
        "appointments": appointments,
        "doctor": doctor,
        "status": {
            "pending": pending_count,
            "confirmed": confirmed_count,
            "rejected": rejected_count,
            "total_patients": total_patients
        }
    })


@login_required
def doctor_patient_detail(request, patient_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.role != 'doctor':
        messages.error(request, "Access denied.")
        return redirect('doctor_appointments')

    patient = get_object_or_404(Patient, id=patient_id)
    health = PatientHealthData.objects.filter(patient=patient).last()
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')

    return render(request, "doctor/patient_detail.html", {
        "patient": patient,
        "health": health,
        "appointments": appointments[:5]
    })


@login_required
def approve_appointment(request, id):
    # BUG FIX: original was Appointment.objects.get(Appointment, id=id, ...) which is wrong syntax
    # Also doctor field is a Doctor FK not User FK
    appointment = get_object_or_404(Appointment, id=id)
    appointment.status = 'Confirmed'
    appointment.save()
    messages.success(request, "Appointment confirmed.")
    return redirect('doctor_appointments')


@login_required
def reject_appointment(request, id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=id)
        reason = request.POST.get("rejection_reason", "").strip()
        appointment.status = "Rejected"
        appointment.rejection_reason = reason
        appointment.save()
        messages.success(request, "Appointment rejected.")
        return redirect("doctor_appointments")
    messages.error(request, "Rejection requires form submission.")
    return redirect("doctor_appointments")


def patient_records(request):
    return render(request, 'doctor/patient_records.html')


def add_prescription(request):
    return render(request, 'doctor/add_prescription.html')


# ===============================
# PATIENT VIEWS
# ===============================

@login_required
def patient_home(request):
    return render(request, "patient/home.html")


@login_required
def patient_dashboard(request):
    patient = get_object_or_404(Patient, user=request.user)
    # BUG FIX: was rendering 'patient/dashboard.html' which does not exist; correct file is patient_dashboard.html
    return render(request, "patient/patient_dashboard.html", {"patient": patient})


@login_required
def book_appointment(request):
    from datetime import date
    doctors = Doctor.objects.all()

    if request.method == "POST":
        doctor_id = request.POST.get("doctor")
        app_date = request.POST.get("date")
        time = request.POST.get("time")

        if not all([doctor_id, app_date, time]):
            messages.error(request, "All fields are required.")
            return render(request, "patient/book_appointment.html", {"doctors": doctors})

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            patient = Patient.objects.get(user=request.user)
            app_date_obj = date.fromisoformat(app_date)

            if app_date_obj < date.today():
                messages.error(request, "Cannot book appointment in the past.")
                return render(request, "patient/book_appointment.html", {"doctors": doctors})

            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_date=app_date,
                appointment_time=time
            )
            messages.success(request, "Appointment booked successfully!")
            return redirect("appointment_history")
        except Doctor.DoesNotExist:
            messages.error(request, "Invalid doctor selected.")
        except Patient.DoesNotExist:
            messages.error(request, "Patient profile not found.")

    return render(request, "patient/book_appointment.html", {"doctors": doctors})


@login_required
def appointment_history(request):
    patient = get_object_or_404(Patient, user=request.user)
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    return render(request, "patient/appointment_history.html", {"appointments": appointments})


@login_required
def health_library(request):
    if request.method == "POST":
        patient = get_object_or_404(Patient, user=request.user)
        PatientHealthData.objects.create(
            patient=patient,
            age=request.POST.get("age"),
            gender=request.POST.get("gender"),
            weight=request.POST.get("weight"),
            height=request.POST.get("height"),
            blood_pressure=request.POST.get("blood_pressure"),
            heart_rate=request.POST.get("heart_rate"),
            temperature=request.POST.get("temperature"),
            oxygen_level=request.POST.get("oxygen_level"),
            blood_sugar=request.POST.get("blood_sugar"),
            cholesterol=request.POST.get("cholesterol"),
            hemoglobin=request.POST.get("hemoglobin"),
            symptoms=request.POST.get("symptoms"),
            disease_history=request.POST.get("disease_history"),
            medications=request.POST.get("medications"),
            allergies=request.POST.get("allergies"),
            smoking=request.POST.get("smoking"),
            alcohol=request.POST.get("alcohol"),
            exercise=request.POST.get("exercise"),
            sleep_hours=request.POST.get("sleep_hours"),
            family_diabetes=request.POST.get("family_diabetes"),
            family_heart=request.POST.get("family_heart"),
        )
        return redirect("health_analysis")
    return render(request, "patient/health_library.html")


@login_required
def health_analysis(request):
    patient = get_object_or_404(Patient, user=request.user)
    health = PatientHealthData.objects.filter(patient=patient).last()
    bmi = None
    if health:
        height_m = float(health.height) / 100
        bmi = float(health.weight) / (height_m * height_m)
    context = {
        "health": health,
        "bmi": round(bmi, 2) if bmi else None,
        "bp_risk": int(health.blood_pressure) > 140 if health else False,
        "sugar_risk": float(health.blood_sugar) > 180 if health else False,
        "cholesterol_risk": float(health.cholesterol) > 200 if health else False,
    }
    return render(request, "patient/health_analysis.html", context)


@login_required
def medicine_reminder(request):
    patient = get_object_or_404(Patient, user=request.user)
    if request.method == "POST":
        medicine_name = request.POST.get("medicine_name")
        time = request.POST.get("time")
        days = request.POST.get("days")
        MedicineReminder.objects.create(
            patient=patient,
            medicine_name=medicine_name,
            time=time,
            days=days
        )
        messages.success(request, "Reminder added successfully!")
        return redirect("medicine_reminder")
    reminders = MedicineReminder.objects.filter(patient=patient)
    return render(request, "patient/medicine_reminder.html", {"reminders": reminders})


@login_required
def profile(request):
    patient = get_object_or_404(Patient, user=request.user)
    health = PatientHealthData.objects.filter(patient=patient).last()
    reminders = MedicineReminder.objects.filter(patient=patient)
    return render(request, "patient/profile.html", {
        "patient": patient,
        "health": health,
        "reminders": reminders
    })


# ===============================
# LAB VIEWS
# ===============================

def lab_dashboard(request):
    return render(request, 'lab/lab_dashboard.html')


@login_required
def upload_report(request):
    patients = Patient.objects.all()
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        report_file = request.FILES.get("report")
        patient = get_object_or_404(Patient, id=patient_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)
        MedicalReport.objects.create(
            patient=patient,
            doctor=doctor,
            report_file=report_file
        )
        messages.success(request, "Report uploaded successfully!")
        return redirect("lab_dashboard")
    doctors = Doctor.objects.all()
    return render(request, "lab/upload_report.html", {"patients": patients, "doctors": doctors})


def test_requests(request):
    return render(request, 'lab/test_requests.html')


def lab_tests(request):
    return render(request, "lab/lab_dashboard.html")


# ===============================
# ADMIN VIEWS
# ===============================

@login_required
def admin_dashboard(request):
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()
    total_reports = MedicalReport.objects.count()
    context = {
        "patients": total_patients,
        "doctors": total_doctors,
        "appointments": total_appointments,
        "reports": total_reports,
    }
    return render(request, "admin/admin_dashboard.html", context)


@login_required
def admin_patient_health(request):
    health_data = PatientHealthData.objects.select_related("patient").all().order_by("-id")
    return render(request, "admin/patient_health_data.html", {"health_data": health_data})


# ===============================
# LOGOUT
# ===============================

def logout_view(request):
    logout(request)
    return redirect("login")
