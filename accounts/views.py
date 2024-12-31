from django.shortcuts import render, redirect
from django.contrib.auth.forms import User, AuthenticationForm
from django.contrib import auth

# Create your views here.
def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                auth.login(request, user)
                return redirect('home')
            except:
                return render(request, 'accounts/signup.html', {'error': 'Username already taken'})
        else:
            return render(request, 'accounts/signup.html', {'error': 'Passwords do not match'})
    else:
        return render(request, 'accounts/signup.html')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')