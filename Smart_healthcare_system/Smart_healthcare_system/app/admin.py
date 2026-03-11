from django.contrib import admin

# Register your models here.
from .models import PatientHealthData

from .models import Doctor, Appointment, Patient

admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Patient)

admin.site.register(PatientHealthData)
