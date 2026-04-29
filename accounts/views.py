from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import CustomUser
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import CustomUser, Appointment, Payment
from datetime import date
from datetime import datetime, date
from django.shortcuts import render


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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        print("DEBUG USER:", user)  

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

    return render(request, 'login.html')


@login_required
def doctor_dashboard(request):
    return render(request, 'doctor_dashboard.html')
 

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user)

    paid_appointments = Payment.objects.values_list('appointment_id', flat=True)

    return render(request, 'patient_dashboard.html', {
        'appointments': appointments,
        'paid_appointments': paid_appointments
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

    return render(request, 'admin_dashboard.html')


@login_required
def admin_dashboard(request):
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
    appointments = Appointment.objects.filter(doctor=request.user)

    return render(request, 'doctor_requests.html', {'appointments': appointments})


def approve_appointment(request, id):
    appt = Appointment.objects.get(id=id)
    appt.status = 'approved'
    appt.save()
    return redirect('doctor_requests')


def reject_appointment(request, id):
    appt = Appointment.objects.get(id=id)
    appt.status = 'rejected'
    appt.save()
    return redirect('doctor_requests')



# PAYMENT (AFTER APPROVAL)

@login_required
def make_payment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)

    if request.method == 'POST':
        Payment.objects.create(
            appointment=appointment,
            amount=500,
            is_paid=True
        )
        return redirect('patient_dashboard')

    return render(request, 'payment.html', {
        'appointment': appointment
    })


@login_required
def cancel_appointment(request, id):
    appt = Appointment.objects.get(id=id)

    if appt.patient == request.user:
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