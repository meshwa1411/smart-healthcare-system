from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    address = models.TextField()

    def __str__(self):
        return self.user.username


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, default="0000000000")
    experience = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.patient} - {self.doctor}"

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