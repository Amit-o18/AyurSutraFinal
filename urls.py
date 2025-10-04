from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.auth_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('atss/', views.automated_therapy_scheduling_system, name='atss'),
    # ATSS API endpoints
    path('api/atss/appointments/', views.list_appointments, name='atss_list_appointments'),
    path('api/atss/appointments/create/', views.create_appointment, name='atss_create_appointment'),
    path('api/atss/appointments/<int:appt_id>/cancel/', views.cancel_appointment, name='atss_cancel_appointment'),
    # Therapy progress endpoints
    path('api/atss/progress/', views.list_progress, name='atss_list_progress'),
    path('api/atss/progress/create/', views.create_progress, name='atss_create_progress'),
    path('tips/', views.wellness_tips, name='wellness_tips'),
    # path('rttt/', views.realtime_therapy_tracking, name='realtime_therapy_tracking'),
    path('vt/', views.visualisation_tools, name='visualisation_tools'),
        path('rttt/', views.therapy_tracking_page, name='therapy_tracking'),
]