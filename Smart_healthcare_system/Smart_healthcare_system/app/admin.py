from django.contrib import admin

# Register your models here.
from .models import PatientHealthData

admin.site.register(PatientHealthData)
