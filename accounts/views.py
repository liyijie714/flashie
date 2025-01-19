from django.shortcuts import render, redirect
from django.contrib.auth.forms import User, AuthenticationForm
from django.contrib import auth
from grader.models import Teacher
from django.contrib.auth import authenticate
from django.contrib import messages

# Create your views here.
def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.get(username=request.POST['username'])
                return render(request, 'accounts/signup.html', {'error': 'Username has already been taken'})
            except User.DoesNotExist:
                try:
                    user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password1'])
                    messages.success(request, 'Account created successfully. Please log in.')
                    return redirect('accounts:login')
                except Exception as e:
                    messages.error(request, str(e))
                    return render(request, 'accounts/signup.html')
        else:
            return render(request, 'accounts/signup.html', {'error': 'Passwords must match'})
    else:
        return render(request, 'accounts/signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('products:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('products:home')
    return redirect('products:home')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return render(request, 'accounts/profile.html')
    