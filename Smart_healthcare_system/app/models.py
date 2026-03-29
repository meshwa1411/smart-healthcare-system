from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('lab', 'Lab Staff'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default="0000000000")
    age = models.IntegerField(default=0)
    gender = models.CharField(max_length=10, default="Unknown")
    address = models.TextField(default="Not Provided")

    def __str__(self):
        return self.user.username


# class Doctor(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     specialization = models.CharField(max_length=100, default="General")
#     phone = models.CharField(max_length=15, default="0000000000")

#     def __str__(self):
#         return self.user.username
class Doctor(models.Model):

    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100,default="General")
    experience = models.IntegerField()
    hospital = models.CharField(max_length=200)

    available_days = models.CharField(max_length=100)
    available_time = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# class Appointment(models.Model):

#     STATUS_CHOICES = (
#         ('Pending', 'Pending'),
#         ('Approved', 'Approved'),
#         ('Rejected', 'Rejected'),
#     )

#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
#     doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
#     # appointment_date = models.DateField()
#     appointment_time = models.TimeField()
#     date = models.DateField()
#     time = models.TimeField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

#     def __str__(self):
#         return f"{self.patient} - {self.doctor}"

# class Appointment(models.Model):

#     patient = models.ForeignKey(Patient,on_delete=models.CASCADE)
#     doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)

#     appointment_date = models.DateField()
#     appointment_time = models.TimeField()

#     status = models.CharField(max_length=20,default="Pending", choices=(('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Rejected', 'Rejected')))
    
#     rejection_reason = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.patient} - {self.doctor}"

from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} → {self.doctor.username}"
    
class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    medicine = models.TextField()
    notes = models.TextField()

    def __str__(self):
        return f"Prescription for {self.appointment.patient}"


class LabReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=100)
    report_file = models.FileField(upload_to='reports/')
    date = models.DateField()

    def __str__(self):
        return self.test_name
    
class MedicalReport(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    report_file = models.FileField(upload_to="reports/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient)
    
    



class PatientHealthData(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)

    weight = models.FloatField()
    height = models.FloatField()

    blood_pressure = models.IntegerField()
    heart_rate = models.IntegerField()

    temperature = models.FloatField()
    oxygen_level = models.IntegerField()

    blood_sugar = models.FloatField()
    cholesterol = models.FloatField()
    hemoglobin = models.FloatField()

    symptoms = models.TextField()
    disease_history = models.TextField()

    medications = models.TextField()
    allergies = models.TextField()

    smoking = models.CharField(max_length=10)
    alcohol = models.CharField(max_length=10)
    exercise = models.CharField(max_length=20)

    sleep_hours = models.IntegerField()

    family_diabetes = models.CharField(max_length=10)
    family_heart = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.patient.user.username
    
class MedicineReminder(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    medicine_name = models.CharField(max_length=100)

    time = models.TimeField()

    days = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.medicine_name