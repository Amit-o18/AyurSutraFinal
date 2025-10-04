from django.shortcuts import render, redirect
from .models import WellnessTip, Profile, PractitionerProfile
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    return render(request, 'home.html')

def automated_therapy_scheduling_system(request):
    return render(request, 'automated-therapy-scheduling-system.html')

def wellness_tips(request):
    # Fetch all tips as a list
    tips = list(WellnessTip.objects.all())
    context = {
        "tips": tips
    }
    return render(request, "wellness-tips.html", context)

def realtime_therapy_tracking(request):
    return render(request, 'realtime-therapy-tracking.html')


from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Appointment
from .models import TherapyProgress


def automated_therapy_scheduling_system(request):
    # render the template that contains the frontend scheduler
    return render(request, 'automated-therapy-scheduling-system.html')


def _serialize_appt(a: Appointment):
    return {
        'id': a.id,
        'patient': a.patient_name,
        'therapy': a.therapy_type,
        'date': a.date.isoformat(),
        'time': a.time,
        'canceled': a.canceled,
    }


def _serialize_progress(p: TherapyProgress):
    return {
        'id': p.id,
        'patient': p.patient_name,
        'date': p.date.isoformat(),
        'mood_score': float(p.mood_score) if p.mood_score is not None else None,
        'progress_percent': p.progress_percent,
        'session_completed': p.session_completed,
        'notes': p.notes,
        'created_at': p.created_at.isoformat(),
    }


def list_progress(request):
    """Return JSON list of therapy progress entries. Optional filters: patient, date"""
    patient = request.GET.get('patient')
    date = request.GET.get('date')
    qs = TherapyProgress.objects.all().order_by('-date', '-created_at')
    if patient:
        qs = qs.filter(patient_name__icontains=patient)
    if date:
        qs = qs.filter(date=date)
    items = [_serialize_progress(p) for p in qs[:200]]
    return JsonResponse({'progress': items})


@csrf_exempt
def create_progress(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    try:
        data = json.loads(request.body.decode('utf-8'))
        patient = data.get('patient')
        date = data.get('date')
        mood = data.get('mood_score')
        percent = data.get('progress_percent')
        session_completed = bool(data.get('session_completed'))
        notes = data.get('notes') or ''
        if not all((patient, date)):
            return HttpResponseBadRequest('missing field')
        tp = TherapyProgress.objects.create(
            patient_name=patient,
            date=date,
            mood_score=(None if mood in (None, '') else float(mood)),
            progress_percent=(None if percent in (None, '') else int(percent)),
            session_completed=session_completed,
            notes=notes,
        )
        return JsonResponse({'progress': _serialize_progress(tp)}, status=201)
    except Exception as e:
        logger.exception('create progress failed: %s', e)
        return JsonResponse({'error': 'server_error'}, status=500)


def list_appointments(request):
    # optional filter by date via ?date=YYYY-MM-DD
    date = request.GET.get('date')
    qs = Appointment.objects.filter(canceled=False)
    if date:
        qs = qs.filter(date=date)
    items = [_serialize_appt(a) for a in qs.order_by('date', 'time')]
    return JsonResponse({'appointments': items})


@csrf_exempt
def create_appointment(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    try:
        data = json.loads(request.body.decode('utf-8'))
        patient = data.get('patient')
        therapy = data.get('therapy')
        date = data.get('date')
        time = data.get('time')
        if not all((patient, therapy, date, time)):
            return HttpResponseBadRequest('missing field')
        # basic validation
        patient = patient.strip()
        if len(patient) < 2:
            return JsonResponse({'error': 'invalid_patient'}, status=400)

        # check duplicate slot for the same date+time (prevent double-booking)
        if Appointment.objects.filter(date=date, time=time, canceled=False).exists():
            return JsonResponse({'error': 'slot_taken'}, status=400)

        appt = Appointment.objects.create(patient_name=patient, therapy_type=therapy, date=date, time=time)
        return JsonResponse({'appointment': _serialize_appt(appt)}, status=201)
    except Exception as e:
        logger.exception('create appointment failed: %s', e)
        return JsonResponse({'error': 'server_error'}, status=500)


@csrf_exempt
def cancel_appointment(request, appt_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    try:
        appt = Appointment.objects.filter(id=appt_id).first()
        if not appt:
            return JsonResponse({'error': 'not_found'}, status=404)
        appt.canceled = True
        appt.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        logger.exception('cancel appointment failed: %s', e)
        return JsonResponse({'error': 'server_error'}, status=500)


# Combined auth view for signup & login using the `login-signup.html` template
@require_http_methods(["GET", "POST"])
def auth_view(request):
    if request.method == "GET":
        return render(request, 'login-signup.html')

    post = request.POST

    # SIGNUP flow
    if 'fullname' in post:
        fullname = post.get('fullname', '').strip()
        email = post.get('email', '').strip().lower()
        password = post.get('password', '')
        password_confirm = post.get('confirm-password', '')

        # patient fields
        age = post.get('age') or None
        gender = post.get('gender') or None
        medical_id = post.get('medical-id') or None

        # practitioner fields
        specialization = post.get('specialization') or None
        experience = post.get('experience') or None
        license_no = post.get('license') or None
        clinic = post.get('clinic') or None

        if not fullname or not email or not password:
            messages.error(request, "Name, email and password are required.")
            return render(request, 'login-signup.html')

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'login-signup.html')

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken.")
            return render(request, 'login-signup.html')

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=email, email=email, password=password, first_name=fullname)

                # Persist profile fields explicitly
                from .models import Profile as ProfileModel, PractitionerProfile as PractitionerModel, LegacyUser
                ProfileModel.objects.update_or_create(
                    user=user,
                    defaults={
                        'age': int(age) if age else None,
                        'gender': gender if gender else None,
                        'medical_id': medical_id if medical_id else None,
                    }
                )

                # Persist practitioner fields only if any provided
                if any((specialization, experience, license_no, clinic)):
                    PractitionerModel.objects.update_or_create(
                        user=user,
                        defaults={
                            'specialization': specialization or None,
                            'experience': int(experience) if experience else None,
                            'license_number': license_no or None,
                            'clinic': clinic or None,
                        }
                    )

                # Also insert into the legacy `users` table (hashed password)
                from django.contrib.auth.hashers import make_password
                hashed = make_password(password)
                try:
                    LegacyUser.objects.create(
                        name=fullname,
                        email=email,
                        password=hashed,
                        age=int(age) if age else None,
                        gender=(gender.title() if gender else 'Other'),
                        medical_id=medical_id or None
                    )
                except Exception as e:
                    # If legacy insert fails, log but continue. The primary Django user exists.
                    logger.exception("Failed to create legacy user row for %s: %s", email, e)
        except Exception:
            messages.error(request, "Could not create account. Try again.")
            return render(request, 'login-signup.html')

        # Successful signup: log the user in and redirect home
        login(request, user)
        messages.success(request, "Account created and logged in.")
        logger.info("Signup successful for %s", email)
        return redirect('/')

    # LOGIN flow
    elif 'login-email' in post:
        email = post.get('login-email', '').strip().lower()
        password = post.get('login-password', '')

        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.error(request, "Invalid credentials.")
            return render(request, 'login-signup.html')

        # Successful login: log the user in and redirect home
        login(request, user)
        messages.success(request, "Logged in.")
        logger.info("Login successful for %s", email)
        return redirect('/')

    # unknown submission
    messages.error(request, "Invalid form submission.")
    return render(request, 'login-signup.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('auth')


@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    practitioner = getattr(request.user, 'practitioner', None)
    context = {
        'user': request.user,
        'profile': profile,
        'practitioner': practitioner
    }
    return render(request, 'profile.html', context)

def visualisation_tools(request):
    return render(request, 'visualisationtools.html')


def therapy_tracking_page(request):
    """Render the therapy tracking dashboard."""
    return render(request, 'therapy-tracking.html')


