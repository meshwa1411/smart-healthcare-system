from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_page, name='login'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Patient
    path('home/', views.patient_home, name='patient_home'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointment-history/', views.appointment_history, name='appointment_history'),
    path('health-library/', views.health_library, name='health_library'),
    path('health-analysis/', views.health_analysis, name='health_analysis'),
    path('medicine-reminder/', views.medicine_reminder, name='medicine_reminder'),
    path('profile/', views.profile, name='profile'),

    # Doctor
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor-appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor-patient-detail/<int:patient_id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
    path('approve-appointment/<int:id>/', views.approve_appointment, name='approve_appointment'),
    path('reject-appointment/<int:id>/', views.reject_appointment, name='reject_appointment'),
    path('patient-records/', views.patient_records, name='patient_records'),
    path('add-prescription/', views.add_prescription, name='add_prescription'),

    # Lab
    path('lab/dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path('upload-report/', views.upload_report, name='upload_report'),
    path('test-requests/', views.test_requests, name='test_requests'),
    path('lab-tests/', views.lab_tests, name='lab_tests'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-patient-health/', views.admin_patient_health, name='admin_patient_health'),
]
