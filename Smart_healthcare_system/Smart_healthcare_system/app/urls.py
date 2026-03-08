from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
     path('admin/', admin.site.urls),

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
]