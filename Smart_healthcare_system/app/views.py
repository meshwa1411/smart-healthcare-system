from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .models import Doctor, Appointment, Patient,UserProfile,MedicalReport,PatientHealthData,MedicineReminder
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



def home(request):
    return render(request, 'home.html')


def login_page(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            profile = UserProfile.objects.get(user=user)

            # PATIENT → HOME PAGE
            if profile.role == "patient":
                return redirect("patient_home")

            # DOCTOR → DOCTOR DASHBOARD
            elif profile.role == "doctor":
                return redirect("doctor_dashboard")

            # LAB → LAB DASHBOARD
            elif profile.role == "lab":
                return redirect("lab_dashboard")

            # ADMIN → ADMIN DASHBOARD
            elif profile.role == "admin":
                return redirect("admin_dashboard")

        else:
            return render(request, "login.html", {"error": "Invalid Credentials"})

    return render(request, "login.html")
def register_page(request):

    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role=role
        )

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

        messages.success(request, "Account created successfully")

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


# def patient_dashboard(request):
#     return render(request, 'patient/dashboard.html')


# @login_required
# def doctor_dashboard(request):
#     return redirect('doctor_appointments')
@login_required
def doctor_dashboard(request):
    appointments = Appointment.objects.filter(doctor=request.user)

    status = {
        'pending': appointments.filter(status='Pending').count(),
        'confirmed': appointments.filter(status='Confirmed').count(),
        'rejected': appointments.filter(status='Rejected').count(),
        'total_patients': appointments.values('patient').distinct().count()
    }

    return render(request, 'doctor/doctor_dashboard.html', {
        'appointments': appointments,
        'status': status,
        'doctor': request.user
    })


def lab_dashboard(request):
    return render(request, 'lab/dashboard.html')

def admin_dashboard(request):
    return render(request,"admin/admin_dashboard.html")

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
def doctor_appointments(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'doctor':
        messages.error(request, "Access denied. Doctors only.")
        return redirect('patient_home')
    
    try:
        doctor = Doctor.objects.get(name=request.user.username)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('home')
    
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')
    
    # Stats
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
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'doctor':
        messages.error(request, "Access denied.")
        return redirect('doctor_appointments')
    
    patient = Patient.objects.get(id=patient_id)
    health = PatientHealthData.objects.filter(patient=patient).last()
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    
    return render(request, "doctor/patient_detail.html", {
        "patient": patient,
        "health": health,
        "appointments": appointments[:5]  # Last 5
    })
@login_required
def appointment_history(request):

    patient = Patient.objects.get(user=request.user)
    appointments = Appointment.objects.filter(patient=patient)

    return render(request, "patient/appointment_history.html", {
        "appointments": appointments
    })
# @login_required
# def approve_appointment(request, id):

#     appointment = Appointment.objects.get(id=id)
#     appointment.status = "Approved"
#     appointment.save()

#     return redirect("doctor_appointments")

@login_required
def approve_appointment(request, id):
    appointment =Appointment.objects.get(Appointment, id=id, doctor=request.user)
    appointment.status = 'Confirmed'
    appointment.save()
    return redirect('doctor_dashboard')

@login_required
def reject_appointment(request, id):
    if request.method == "POST":
        appointment = Appointment.objects.get(id=id)
        reason = request.POST.get("rejection_reason", "").strip()
        appointment.status = "Rejected"
        appointment.rejection_reason = reason
        appointment.save()
        messages.success(request, "Appointment rejected.")
        return redirect("doctor_appointments")
    
    # For GET, could render form but redirect for simplicity
    messages.error(request, "Rejection requires form submission.")
    return redirect("doctor_appointments")

@login_required
def upload_report(request):

    patients = Patient.objects.all()

    if request.method == "POST":

        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        report_file = request.FILES.get("report")

        patient = Patient.objects.get(id=patient_id)
        doctor = Doctor.objects.get(id=doctor_id)

        MedicalReport.objects.create(
            patient=patient,
            doctor=doctor,
            report_file=report_file
        )

        return redirect("lab_dashboard")

    doctors = Doctor.objects.all()

    return render(request, "lab/upload_report.html", {
        "patients": patients,
        "doctors": doctors
    })
    
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
def patient_home(request):

    return render(request, "patient/home.html")

@login_required
def patient_dashboard(request):

    patient = Patient.objects.get(user=request.user)

    return render(request, "patient/dashboard.html", {
        "patient": patient
    })
    

def patient_records(request):
    return render(request,'doctor/patient_records.html')

def add_prescription(request):
    return render(request,'doctor/add_prescription.html')

# def upload_report(request):
#     return render(request,'lab/upload_report.html')

def test_requests(request):
    return render(request,'lab/test_requests.html') 



@login_required
def health_library(request):

    if request.method == "POST":

        patient = Patient.objects.get(user=request.user)

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


# @login_required
# def health_analysis(request):

#     health = PatientHealthData.objects.filter(patient=request.user).last()

#     bp_risk = False
#     sugar_risk = False
#     cholesterol_risk = False

#     if health:

#         if health.blood_pressure and int(health.blood_pressure) > 140:
#             bp_risk = True

#         if health.blood_sugar and float(health.blood_sugar) > 126:
#             sugar_risk = True

#         if health.cholesterol and float(health.cholesterol) > 200:
#             cholesterol_risk = True

#     context = {
#         "health": health,
#         "bp_risk": bp_risk,
#         "sugar_risk": sugar_risk,
#         "cholesterol_risk": cholesterol_risk
#     }

#     return render(request, "patient/health_analysis.html", context)

def lab_tests(request):
    return render(request, "lab/lab_dashboard.html")

@login_required
def admin_patient_health(request):

    health_data = PatientHealthData.objects.select_related("patient").all().order_by("-id")

    return render(request, "admin/patient_health_data.html", {
        "health_data": health_data
    })
    
@login_required
def medicine_reminder(request):

    patient = Patient.objects.get(user=request.user)

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

        return redirect("medicine_reminder")

    reminders = MedicineReminder.objects.filter(patient=patient)

    return render(request, "patient/medicine_reminder.html", {
        "reminders": reminders
    })
    
    
@login_required
def health_analysis(request):

    patient = Patient.objects.get(user=request.user)

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


# ===============================
# PROFILE PAGE
# ===============================

@login_required
def profile(request):

    patient = Patient.objects.get(user=request.user)

    health = PatientHealthData.objects.filter(patient=patient).last()

    reminders = MedicineReminder.objects.filter(patient=patient)

    return render(request,"patient/profile.html",{
        "patient":patient,
        "health":health,
        "reminders":reminders
    })


# ===============================
# LOGOUT
# ===============================

def logout_view(request):
     logout(request)
     return redirect("login")