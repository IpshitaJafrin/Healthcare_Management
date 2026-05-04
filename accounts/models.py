from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15)

    # Doctor-specific
    specialization = models.CharField(max_length=100, blank=True, null=True)

    # Patient-specific
    age = models.IntegerField(blank=True, null=True)

    # Common profile fields
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', default='default.png')

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'patient'}
    )

    doctor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'doctor'}
    )

    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} → {self.doctor.username} ({self.status})"


class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    amount = models.FloatField(default=500)
    is_paid = models.BooleanField(default=False)

    
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.appointment}"


class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='prescriptions_created', limit_choices_to={'role': 'doctor'})
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='prescriptions_received', limit_choices_to={'role': 'patient'})
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    prescription_file = models.FileField(upload_to='prescriptions/')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription: {self.title} - {self.patient.username} by Dr. {self.doctor.username}"