from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import NewUser
from django.db import IntegrityError

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import NewUser
from django.db import IntegrityError
from django.contrib.auth.views import PasswordResetConfirmView
from .forms import CustomSetPasswordForm



def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mat_no = request.POST.get('mat_no')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')

        # Check if email or mat_no already exists
        if NewUser.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error_message': 'Email already exists'})
        if NewUser.objects.filter(mat_no=mat_no).exists():
            return render(request, 'signup.html', {'error_message': 'Matric number already exists'})

        try:
            user = NewUser.objects.create_user(
                mat_no=mat_no,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
            )
            return redirect('login')

        except IntegrityError:
            return render(request, 'signup.html', {'error_message': 'An error occurred. Please try again.'})

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not NewUser.objects.filter(email=email).exists():
            return render(request, 'login.html', {'error_message': 'Email not found'})

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error_message': 'Incorrect password'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not NewUser.objects.filter(email=email).exists():
            return render(request, 'login.html', {'error_message': 'Email not found'})

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error_message': 'Incorrect password'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def forgot_view(request):
    user = request.user
    context = {
        'user':user,
    }
    return render(request, context, 'forgot.html')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'custom_reg/password_reset_confirm.html'
