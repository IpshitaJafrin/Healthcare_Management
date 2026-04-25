from django.contrib.auth.models import AbstractUser
from django.db import models

from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15)

    # Doctor fields
    specialization = models.CharField(max_length=100, blank=True, null=True)

    # Patient fields
    age = models.IntegerField(blank=True, null=True)

    is_verified = models.BooleanField(default=False)



  

User = settings.AUTH_USER_MODEL


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')

    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.status})"


class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    amount = models.FloatField(default=500)
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)