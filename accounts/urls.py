from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),   # homepage
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('logout/', views.user_logout, name='logout'),

]