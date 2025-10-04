from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
	list_display = ('patient_name', 'therapy_type', 'date', 'time', 'canceled', 'created_at')
	list_filter = ('therapy_type', 'date', 'canceled')
	search_fields = ('patient_name',)

from .models import TherapyProgress


@admin.register(TherapyProgress)
class TherapyProgressAdmin(admin.ModelAdmin):
	list_display = ('patient_name', 'date', 'mood_score', 'progress_percent', 'session_completed', 'created_at')
	list_filter = ('session_completed','date')
	search_fields = ('patient_name','notes')
