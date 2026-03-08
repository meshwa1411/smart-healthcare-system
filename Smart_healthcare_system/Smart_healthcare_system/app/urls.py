from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

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
path('approve-appointment/<int:id>/', views.approve_appointment, name='approve_appointment'),
path('reject-appointment/<int:id>/', views.reject_appointment, name='reject_appointment'),

# PATIENT
    path('home/', views.patient_home, name='patient_home'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path("health-library/", views.health_library, name="health_library"),
    path("health-analysis/", views.health_analysis, name="health_analysis"),

# DOCTOR
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

# LAB
    path('lab-dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path("lab-tests/", views.lab_tests, name="lab_tests"),


]