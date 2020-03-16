from django.contrib import admin
from .models import Patient, TumorTarget, TargetImage

admin.site.register(Patient)
admin.site.register(TumorTarget)
admin.site.register(TargetImage)