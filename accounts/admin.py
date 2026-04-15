from django.contrib import admin

from .models import CustomUser


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
