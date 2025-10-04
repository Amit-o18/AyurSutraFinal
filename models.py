from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class WellnessTip(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        db_table = 'wellness_tips'
        # set to True so Django can manage migrations for this table
        managed = True

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    medical_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return getattr(self.user, 'get_full_name', lambda: str(self.user))()


class PractitionerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practitioner')
    specialization = models.CharField(max_length=255, null=True, blank=True)
    experience = models.PositiveIntegerField(null=True, blank=True)
    license_number = models.CharField(max_length=255, null=True, blank=True)
    clinic = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Practitioner: {getattr(self.user, 'get_full_name', lambda: str(self.user))()}"


@receiver(post_save, sender=get_user_model())
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        PractitionerProfile.objects.get_or_create(user=instance)


class LegacyUser(models.Model):
    """Model mapped to the existing legacy `users` table in the Ayursutra database.

    Columns expected:
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      email VARCHAR(150) NOT NULL UNIQUE,
      password VARCHAR(255) NOT NULL,
      age INT CHECK (age >= 0),
      gender ENUM('Male', 'Female', 'Other') NOT NULL,
      medical_id VARCHAR(50) DEFAULT NULL
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    medical_id = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'users'
        managed = False  # table exists outside Django migrations

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Appointment(models.Model):
    THERAPY_CHOICES = [
        ('Abhyanga', 'Abhyanga'),
        ('Swedana', 'Swedana'),
        ('Vamana', 'Vamana'),
        ('Virechana', 'Virechana'),
        ('Basti', 'Basti'),
    ]

    patient_name = models.CharField(max_length=150)
    therapy_type = models.CharField(max_length=50, choices=THERAPY_CHOICES)
    date = models.DateField()
    time = models.CharField(max_length=10)  # store as 'HH:MM'
    created_at = models.DateTimeField(auto_now_add=True)
    canceled = models.BooleanField(default=False)

    class Meta:
        db_table = 'appointments'

    def __str__(self):
        return f"{self.patient_name} — {self.date} {self.time} ({self.therapy_type})"


class TherapyProgress(models.Model):
    """Store periodic therapy tracking/progress entries for a patient."""
    patient_name = models.CharField(max_length=150)
    # optional link to authenticated user if available
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField()
    mood_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)  # e.g., 7.8
    progress_percent = models.PositiveSmallIntegerField(null=True, blank=True)
    session_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'therapy_progress'

    def __str__(self):
        return f"{self.patient_name} — {self.date} ({self.mood_score or ''})"


