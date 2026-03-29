from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
#  path('admin/', admin.site.urls),
    path('', views.login_page, name='login'),   # FIRST PAGE
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),

    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('lab/dashboard/', views.lab_dashboard, name='lab_dashboard'),

    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointment-history/', views.appointment_history, name='appointment_history'),
path('patient-records/', views.patient_records),
path('add-prescription/', views.add_prescription),

path('upload-report/', views.upload_report),
path('test-requests/', views.test_requests),

path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('doctor-appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor-patient-detail/<int:patient_id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
path('approve-appointment/<int:id>/', views.approve_appointment, name='approve_appointment'),
path('reject-appointment/<int:id>/', views.reject_appointment, name='reject_appointment'),

# PATIENT
    path('home/', views.patient_home, name='patient_home'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path("health-library/", views.health_library, name="health_library"),
    path("health-analysis/", views.health_analysis, name="health_analysis"),

# DOCTOR
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
        path('approve/<int:id>/', views.approve_appointment, name='approve_appointment'),
    path('reject/<int:id>/', views.reject_appointment, name='reject_appointment'),
    path('patient-detail/<int:id>/', views.doctor_patient_detail, name='doctor_patient_detail'),


# LAB
    path('lab-dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path("lab-tests/", views.lab_tests, name="lab_tests"),

path("health-library/", views.health_library, name="health_library"),
path("health-analysis/", views.health_analysis, name="health_analysis"),
path("admin-patient-health/", views.admin_patient_health, name="admin_patient_health"),
path("medicine-reminder/", views.medicine_reminder, name="medicine_reminder"),
path('profile/', views.profile, name='profile'),
path('logout/', views.logout_view, name='logout'),
]