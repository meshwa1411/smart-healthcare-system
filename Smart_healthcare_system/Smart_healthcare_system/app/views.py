from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .models import Doctor, Appointment, Patient,UserProfile,MedicalReport
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
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
            Doctor.objects.create(user=user)

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


def patient_dashboard(request):
    return render(request, 'patient/dashboard.html')


def doctor_dashboard(request):
    return render(request, 'doctor/dashboard.html')


def lab_dashboard(request):
    return render(request, 'lab/dashboard.html')

def admin_dashboard(request):
    return render(request,"admin/admin_dashboard.html")

@login_required
def book_appointment(request):

    doctors = Doctor.objects.all()

    if request.method == "POST":

        doctor_id = request.POST.get("doctor")
        date = request.POST.get("date")
        time = request.POST.get("time")

        doctor = Doctor.objects.get(id=doctor_id)
        patient = Patient.objects.get(user=request.user)

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time
        )

        return redirect("appointment_history")

    return render(request, "patient/book_appointment.html", {"doctors": doctors})
@login_required
def doctor_appointments(request):

    doctor = Doctor.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor)

    return render(request, "doctor/appointments.html", {
        "appointments": appointments
    })
@login_required
def appointment_history(request):

    patient = Patient.objects.get(user=request.user)
    appointments = Appointment.objects.filter(patient=patient)

    return render(request, "patient/appointment_history.html", {
        "appointments": appointments
    })
@login_required
def approve_appointment(request, id):

    appointment = Appointment.objects.get(id=id)
    appointment.status = "Approved"
    appointment.save()

    return redirect("doctor_appointments")

@login_required
def reject_appointment(request, id):

    appointment = Appointment.objects.get(id=id)
    appointment.status = "Rejected"
    appointment.save()

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

    return render(request, "admin/dashboard.html", context)

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

def upload_report(request):
    return render(request,'lab/upload_report.html')

def test_requests(request):
    return render(request,'lab/test_requests.html') 
def health_library(request):
    return render(request, "patient/health_library.html")


def health_analysis(request):
    return render(request, "patient/health_analysis.html")


def lab_tests(request):
    return render(request, "lab/lab_dashboard.html")