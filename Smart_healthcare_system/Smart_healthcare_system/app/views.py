from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .models import Doctor, Appointment, Patient
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login


def home(request):
    return render(request, 'home.html')


def login_page(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.role == "patient":
                return redirect('patient_dashboard')

            elif user.role == "doctor":
                return redirect('doctor_dashboard')

            elif user.role == "lab":
                return redirect('lab_dashboard')

        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

def register_page(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(username=username, password=password)

        patient_group = Group.objects.get(name='Patient')
        user.groups.add(patient_group)

        return redirect('login')

    return render(request, 'register.html')


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
def appointment_history(request):
    patient = Patient.objects.get(user=request.user)
    appointments = Appointment.objects.filter(patient=patient)

    return render(request, "patient/appointment_history.html", {
        "appointments": appointments
    })
    
    
def patient_records(request):
    return render(request,'doctor/patient_records.html')

def add_prescription(request):
    return render(request,'doctor/add_prescription.html')

def upload_report(request):
    return render(request,'lab/upload_report.html')

def test_requests(request):
    return render(request,'lab/test_requests.html')