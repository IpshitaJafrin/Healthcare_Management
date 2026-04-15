from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import CustomUser
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


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

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Role-based redirect
            if user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'patient':
                return redirect('patient_dashboard')
            else:
                return redirect('admin_dashboard')

        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


@login_required
def doctor_dashboard(request):
    return render(request, 'doctor_dashboard.html')
 

def user_logout(request):
    logout(request)
    return redirect('home')

def patient_dashboard(request):
    return render(request, 'patient_dashboard.html')