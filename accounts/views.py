from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import CustomUser, Appointment, Payment, Prescription
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from datetime import date
from datetime import datetime, date
from django.shortcuts import render
import requests
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        role = request.POST['role']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone=phone,
            specialization=request.POST.get('specialization'),
            age=request.POST.get('age')
        )

        return redirect('login')

    return render(request, 'register.html')






def user_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 🚫 Block mismatch FIRST
            if role == "doctor" and user.role != "doctor":
                error = "You are not registered as a doctor."
            elif role == "patient" and user.role != "patient":
                error = "You are not registered as a patient."
            elif role == "admin" and not user.is_superuser:
                error = "You are not an admin."
            else:
                # ✅ Only login if role matches
                login(request, user)

                if role == "doctor":
                    return redirect('doctor_dashboard')
                elif role == "patient":
                    return redirect('patient_dashboard')
                elif role == "admin":
                    return redirect('admin_dashboard')

        else:
            error = "Invalid username or password."

    return render(request, 'login.html', {'error': error})



from datetime import date

@login_required
def doctor_dashboard(request):
    today = date.today()

    total_appointments = Appointment.objects.filter(
        doctor=request.user
    ).count()

    today_patients = Appointment.objects.filter(
        doctor=request.user,
        date=today
    ).count()

    pending_requests = Appointment.objects.filter(
        doctor=request.user,
        status='pending'
    ).count()

    paid_appointments = Appointment.objects.filter(
        doctor=request.user,
        payment__is_paid=True
    ).order_by('-created_at')[:5]

    return render(request, 'doctor_dashboard.html', {
        'total_appointments': total_appointments,
        'today_patients': today_patients,
        'pending_requests': pending_requests,
        'paid_appointments': paid_appointments,
    })
 

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user)

    paid_appointments = Payment.objects.values_list('appointment_id', flat=True)
    prescription_count = Prescription.objects.filter(patient=request.user).count()
    return render(request, 'patient_dashboard.html', {
        'appointments': appointments,
        'paid_appointments': paid_appointments,
        'prescription_count': prescription_count
    
    })




# views.py

@login_required
def verify_doctors(request):
    if not request.user.is_superuser:
        return redirect('login')


    doctors = CustomUser.objects.filter(role='doctor', is_verified=False)
    return render(request, 'verify_doctors.html', {'doctors': doctors})


@login_required
def approve_doctor(request, user_id):
    if not request.user.is_superuser:
        return redirect('login')

    
    doctor = CustomUser.objects.get(id=user_id)
    doctor.is_verified = True
    doctor.save()
    return redirect('verify_doctors')


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    total_doctors = CustomUser.objects.filter(role='doctor').count()
    total_patients = CustomUser.objects.filter(role='patient').count()
    pending_doctors = CustomUser.objects.filter(role='doctor', is_verified=False).count()

    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'pending_doctors': pending_doctors,
    }

    return render(request, 'admin_dashboard.html', context)



# Patient : Book Appoinment








@login_required
def book_appointment(request):
    doctors = CustomUser.objects.filter(role='doctor', is_verified=True)
    error = None

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        time = request.POST.get('time')

        # Validate date
        if not date_str:
            error = "Date is required."
        else:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                # ✅ Prevent past date
                if selected_date < date.today():
                    error = "You cannot select a past date."

            except ValueError:
                error = "Invalid date format."

        # If no error → save appointment
        if not error:
            Appointment.objects.create(
                patient=request.user,
                doctor_id=doctor_id,
                date=date_str,
                time=time
            )
            return redirect('patient_dashboard')

    return render(request, 'book_appointment.html', {
        'doctors': doctors,
        'today': date.today().isoformat(),
        'error': error
    })
   



# DOCTOR: APPROVE / REJECT

@login_required
def doctor_requests(request):
    appointments = Appointment.objects.filter(doctor=request.user, status='pending').order_by('-created_at')

    return render(request, 'doctor_requests.html', {'appointments': appointments})


@login_required
def approve_appointment(request, id):
    appt = get_object_or_404(Appointment, id=id, doctor=request.user)
    appt.status = 'approved'
    appt.save()
    return redirect('doctor_requests')


@login_required
def reject_appointment(request, id):
    appt = get_object_or_404(Appointment, id=id, doctor=request.user)
    appt.status = 'rejected'
    appt.save()
    return redirect('doctor_requests')



# PAYMENT (AFTER APPROVAL)





@login_required
def make_payment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment, id=appointment_id, patient=request.user
    )

    # Only allow payment if approved
   # if appointment.status != 'approved':
    #    return redirect('patient_dashboard')

    if request.method == 'POST':
        # Get custom amount from patient input
        custom_amount = request.POST.get('amount')
        try:
            payment_amount = float(custom_amount) if custom_amount else 500
            if payment_amount <= 0:
                messages.error(request, 'Amount must be greater than 0')
                return redirect('make_payment', appointment_id=appointment_id)
        except ValueError:
            messages.error(request, 'Invalid amount entered')
            return redirect('make_payment', appointment_id=appointment_id)
    else:
        payment_amount = 500

    tran_id = f"APPT_{appointment.id}"

    data = {
        'store_id': 'testbox',
        'store_passwd': 'qwerty',
        'total_amount': payment_amount,
        'currency': 'BDT',
        'tran_id': tran_id,

        'success_url': 'http://127.0.0.1:8000/payment-success/',
        'fail_url': 'http://127.0.0.1:8000/payment-fail/',
        'cancel_url': 'http://127.0.0.1:8000/payment-cancel/',

        # Customer Info
        'cus_name': request.user.username,
        'cus_email': request.user.email or 'test@test.com',
        'cus_phone': request.user.phone,
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',

        # Product Info
        'shipping_method': 'NO',
        'product_name': 'Doctor Appointment',
        'product_category': 'Healthcare',
        'product_profile': 'general',
    }

    url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"

    try:
        response = requests.post(url, data=data)
        result = response.json()

        #  Safe check
        if result.get('status') == 'SUCCESS' and result.get('GatewayPageURL'):
            # Store amount in session for use in payment_success
            request.session[f'payment_amount_{appointment_id}'] = payment_amount
            return redirect(result['GatewayPageURL'])
        else:
            return redirect('payment_fail')

    except Exception as e:
        return redirect('payment_fail')


@csrf_exempt
def payment_success(request):
    from django.utils import timezone
    tran_id = request.POST.get('tran_id')

    # Extract appointment ID
    appointment_id = tran_id.split('_')[1]

    appointment = Appointment.objects.get(id=appointment_id)
    
    # Get amount from session or use default
    payment_amount = request.session.pop(f'payment_amount_{appointment_id}', 500)

    Payment.objects.get_or_create(
        appointment=appointment,
        defaults={
            'amount': payment_amount,
            'is_paid': True,
            'transaction_id': tran_id,
            'paid_at': timezone.now()
        }
    )

    return redirect('patient_dashboard')

def payment_fail(request):
    return render(request, 'payment_fail.html')

def payment_cancel(request):
    return redirect('patient_dashboard')

@login_required
def invoice(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    payment = Payment.objects.get(appointment=appointment)

    return render(request, 'invoice.html', {
        'appointment': appointment,
        'payment': payment
    })






@login_required
def cancel_appointment(request, id):
    appt = get_object_or_404(Appointment, id=id, patient=request.user)
    appt.status = 'cancelled'
    appt.save()
    return redirect('patient_dashboard')

#Profile

@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        user.username = request.POST.get('username') or user.username
        user.phone = request.POST.get('phone') or user.phone
        user.bio = request.POST.get('bio') or user.bio

        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')

        if user.role == 'doctor':
            user.specialization = request.POST.get('specialization')

        elif user.role == 'patient':
            user.age = request.POST.get('age')

        user.save()
        return redirect('profile')

    return render(request, 'profile.html', {'user': user})


@login_required
def doctor_list(request):
    query = request.GET.get('q', '').strip()

    doctors = CustomUser.objects.filter(role='doctor')

    if query:
        doctors = doctors.filter(username__icontains=query)

   # doctors = CustomUser.objects.filter(role='doctor')

    return render(request, 'doctor_list.html', {
        'doctors': doctors,
        'query': query
    })



@login_required
def patient_list(request):
    

    query = request.GET.get('q', '').strip()

    patients = CustomUser.objects.filter(role='patient')

    if query:
        patients = patients.filter(username__icontains=query)

    patients = patients.order_by('username')

    return render(request, 'patient_list.html', {
        'patients': patients,
        'query': query
    })


@login_required
def admin_doctor_list(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    query = request.GET.get('q', '').strip()

    doctors = CustomUser.objects.filter(role='doctor')

    if query:
        doctors = doctors.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(specialization__icontains=query)
        )

    doctors = doctors.order_by('username')

    return render(request, 'admin_doctor_list.html', {
        'doctors': doctors,
        'query': query,
        'total_doctors': doctors.count()
    })


# ==================== NEW FEATURES ====================

#  PATIENT: VIEW ALL APPOINTMENTS
@login_required
def patient_all_appointments(request):
    """Patient can view all their appointments with detailed status"""
    appointments = Appointment.objects.filter(patient=request.user).order_by('-created_at')
    paid_appointments = Payment.objects.filter(appointment__patient=request.user).values_list('appointment_id', flat=True)
    
    context = {
        'appointments': appointments,
        'paid_appointments': paid_appointments,
    }
    return render(request, 'patient_all_appointments.html', context)


#  DOCTOR: VIEW APPROVED APPOINTMENTS
@login_required
def doctor_approved_appointments(request):
    """Doctor can view all approved appointments with patient info"""
    appointments = Appointment.objects.filter(doctor=request.user, status='approved').order_by('-created_at')
    
    context = {
        'appointments': appointments,
    }
    return render(request, 'doctor_approved_appointments.html', context)


#  DOCTOR: UPLOAD PRESCRIPTION
@login_required
def upload_prescription(request, appointment_id):
    """Doctor can upload prescription for a specific appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user, status='approved')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        prescription_file = request.FILES.get('prescription_file')
        
        if title and prescription_file:
            try:
                prescription = Prescription.objects.create(
                    appointment=appointment,
                    doctor=request.user,
                    patient=appointment.patient,
                    title=title,
                    description=description,
                    prescription_file=prescription_file
                )
                messages.success(request, 'Prescription uploaded successfully!')
                return redirect('doctor_approved_appointments')
            except Exception as e:
                messages.error(request, f'Error uploading prescription: {str(e)}')
        else:
            messages.error(request, 'Please provide both title and prescription file.')
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'upload_prescription.html', context)


#  PATIENT: VIEW ALL PRESCRIPTIONS
@login_required
def patient_prescriptions(request):
    """Patient can view all prescriptions from all doctors"""
    prescriptions = Prescription.objects.filter(patient=request.user).order_by('-created_at')
    prescription_count = prescriptions.count()
    
    context = {
        'prescriptions': prescriptions,
        'prescription_count': prescription_count,
    }
    return render(request, 'patient_prescriptions.html', context)


#  DOWNLOAD PRESCRIPTION
@login_required
def download_prescription(request, prescription_id):
    """Patient can download a prescription file"""
    from django.http import FileResponse
    import os
    
    prescription = get_object_or_404(Prescription, id=prescription_id, patient=request.user)
    
    file_path = prescription.prescription_file.path
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return response
    else:
        return redirect('patient_prescriptions')


# ==================== REFUND SYSTEM ====================

@login_required
def request_refund(request, appointment_id):
    """Patient can request a refund for a paid appointment"""
    from django.utils import timezone
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    payment = get_object_or_404(Payment, appointment=appointment)
    
    if not payment.is_paid:
        messages.error(request, 'Cannot request refund for unpaid appointment')
        return redirect('patient_payment_reports')
    
    if payment.refund_status != 'none':
        messages.error(request, 'Refund already requested for this appointment')
        return redirect('patient_payment_reports')
    
    if request.method == 'POST':
        refund_reason = request.POST.get('reason')
        refund_amount = payment.amount
        
        payment.refund_status = 'requested'
        payment.refund_requested_at = timezone.now()
        payment.refund_amount = refund_amount
        payment.refund_reason = refund_reason
        payment.save()
        
        messages.success(request, 'Refund request submitted successfully!')
        return redirect('patient_payment_reports')
    
    return render(request, 'request_refund.html', {'appointment': appointment, 'payment': payment})


@login_required
def admin_refund_requests(request):
    """Admin dashboard to manage refund requests"""
    if not request.user.is_superuser:
        return redirect('login')
    
    refund_requests = Payment.objects.filter(refund_status='requested').order_by('-refund_requested_at')
    
    context = {
        'refund_requests': refund_requests,
    }
    return render(request, 'admin_refund_requests.html', context)


@login_required
def approve_refund(request, payment_id):
    """Admin approves a refund request"""
    from django.utils import timezone
    
    if not request.user.is_superuser:
        return redirect('login')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        admin_notes = request.POST.get('notes')
        
        payment.refund_status = 'approved'
        payment.refund_admin_notes = admin_notes
        payment.refund_processed_at = timezone.now()
        payment.save()
        
        messages.success(request, 'Refund approved successfully!')
        return redirect('admin_refund_requests')
    
    return render(request, 'approve_refund.html', {'payment': payment})


@login_required
def cancel_refund(request, payment_id):
    """Admin rejects/cancels a refund request"""
    from django.utils import timezone
    
    if not request.user.is_superuser:
        return redirect('login')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        admin_notes = request.POST.get('notes')
        
        payment.refund_status = 'rejected'
        payment.refund_admin_notes = admin_notes
        payment.refund_processed_at = timezone.now()
        payment.save()
        
        messages.success(request, 'Refund request cancelled!')
        return redirect('admin_refund_requests')
    
    return render(request, 'cancel_refund.html', {'payment': payment})


# ==================== PAYMENT REPORTS ====================

@login_required
def patient_payment_reports(request):
    """Patient can view all their payment details and refund status"""
    payments = Payment.objects.filter(appointment__patient=request.user).select_related('appointment').order_by('-paid_at')
    
    # Calculate statistics
    total_paid = sum(p.amount for p in payments if p.is_paid)
    total_refunded = sum(p.refund_amount for p in payments if p.refund_status == 'approved')
    pending_refunds = payments.filter(refund_status='requested').count()
    
    context = {
        'payments': payments,
        'total_paid': total_paid,
        'total_refunded': total_refunded,
        'pending_refunds': pending_refunds,
    }
    return render(request, 'patient_payment_reports.html', context)


@login_required
def admin_payment_reports(request):
    """Admin can view all payments and refund requests from all patients"""
    if not request.user.is_superuser:
        return redirect('login')
    
    payments = Payment.objects.all().select_related('appointment__patient', 'appointment__doctor').order_by('-paid_at')
    
    # Apply filters
    patient_filter = request.GET.get('patient')
    doctor_filter = request.GET.get('doctor')
    refund_status_filter = request.GET.get('refund_status')
    
    if patient_filter:
        payments = payments.filter(appointment__patient__username__icontains=patient_filter)
    
    if doctor_filter:
        payments = payments.filter(appointment__doctor__username__icontains=doctor_filter)
    
    if refund_status_filter:
        payments = payments.filter(refund_status=refund_status_filter)
    
    # Calculate statistics
    total_revenue = sum(p.amount for p in payments if p.is_paid)
    total_refunds = sum(p.refund_amount for p in payments if p.refund_status == 'approved')
    pending_refunds = payments.filter(refund_status='requested').count()
    approved_refunds = payments.filter(refund_status='approved').count()
    
    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'total_refunds': total_refunds,
        'pending_refunds': pending_refunds,
        'approved_refunds': approved_refunds,
    }
    return render(request, 'admin_payment_reports.html', context)


# ==================== CONSULTATION STATUS ====================

@login_required
def mark_consultation_done(request, appointment_id):
    """Doctor marks an appointment as consulted/completed"""
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    
    appointment.consultation_status = 'consulted'
    appointment.save()
    
    messages.success(request, 'Appointment marked as consulted!')
    return redirect('doctor_approved_appointments')


@login_required
def doctor_consulted_appointments(request):
    """Doctor can view all consulted appointments"""
    appointments = Appointment.objects.filter(
        doctor=request.user,
        status='approved',
        consultation_status='consulted'
    ).order_by('-created_at')
    
    context = {
        'appointments': appointments,
    }
    return render(request, 'doctor_consulted_appointments.html', context)