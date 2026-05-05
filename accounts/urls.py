from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),   # homepage
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('verify_doctors/', views.verify_doctors, name='verify_doctors'),
    path('approve-doctor/<int:user_id>/', views.approve_doctor, name='approve_doctor'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),

    path('doctor-requests/', views.doctor_requests, name='doctor_requests'),
    path('approve-appointment/<int:id>/', views.approve_appointment, name='approve_appointment'),
    path('reject-appointment/<int:id>/', views.reject_appointment, name='reject_appointment'),
    path('cancel-appointment/<int:id>/', views.cancel_appointment, name='cancel_appointment'),
    path('payment/<int:appointment_id>/', views.make_payment, name='make_payment'),
    path('profile/', views.profile, name='profile'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('patients/', views.patient_list, name='patient_list'),
    path('admin-doctors/', views.admin_doctor_list, name='admin_doctor_list'),
    path('invoice/<int:appointment_id>/', views.invoice, name='invoice'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-fail/', views.payment_fail, name='payment_fail'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    
    
    path('appointments/all/', views.patient_all_appointments, name='patient_all_appointments'),
    path('doctor-appointments/approved/', views.doctor_approved_appointments, name='doctor_approved_appointments'),
    path('prescription/upload/<int:appointment_id>/', views.upload_prescription, name='upload_prescription'),
    path('prescriptions/', views.patient_prescriptions, name='patient_prescriptions'),
    path('prescription/download/<int:prescription_id>/', views.download_prescription, name='download_prescription'),
    
    # Refund routes
    path('refund/request/<int:appointment_id>/', views.request_refund, name='request_refund'),
    path('admin-refund-requests/', views.admin_refund_requests, name='admin_refund_requests'),
    path('admin-refund/approve/<int:payment_id>/', views.approve_refund, name='approve_refund'),
    path('admin-refund/cancel/<int:payment_id>/', views.cancel_refund, name='cancel_refund'),
    
    # Payment reports routes
    path('payment-reports/', views.patient_payment_reports, name='patient_payment_reports'),
    path('admin-payment-reports/', views.admin_payment_reports, name='admin_payment_reports'),
    
    # Consultation routes
    path('consultation/mark-done/<int:appointment_id>/', views.mark_consultation_done, name='mark_consultation_done'),
    path('doctor-appointments/consulted/', views.doctor_consulted_appointments, name='doctor_consulted_appointments'),
]

