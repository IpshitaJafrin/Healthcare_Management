from django.contrib import admin

from .models import CustomUser, Appointment, Payment, Prescription


# ================= CUSTOM USER ADMIN =================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):

    # What shows in list view
    list_display = ('id', 'username', 'email', 'role', 'phone', 'is_staff', 'is_active')

    # Search bar
    search_fields = ('username', 'email', 'phone')

    # Filters (right side)
    list_filter = ('role', 'is_staff', 'is_active')


    # Optional ordering
    ordering = ('id',)


# ================= APPOINTMENT ADMIN =================
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'time', 'status', 'created_at')
    search_fields = ('patient__username', 'doctor__username')
    list_filter = ('status', 'date', 'created_at')
    ordering = ('-created_at',)


# ================= PAYMENT ADMIN =================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'amount', 'is_paid', 'paid_at')
    search_fields = ('appointment__patient__username', 'transaction_id')
    list_filter = ('is_paid', 'paid_at')
    ordering = ('-paid_at',)


# ================= PRESCRIPTION ADMIN =================
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'doctor', 'patient', 'created_at')
    search_fields = ('title', 'doctor__username', 'patient__username')
    list_filter = ('created_at', 'doctor')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
