from django.shortcuts import render, redirect
from django.contrib.auth.forms import User, AuthenticationForm
from django.contrib import auth
from grader.models import Teacher

# Create your views here.
def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.get(username=request.POST['username'])
                return render(request, 'accounts/signup.html', {'error': 'Username has already been taken'})
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1'],
                    email=request.POST['email']
                )
                
                # Create teacher profile if checkbox is checked
                if request.POST.get('is_teacher'):
                    Teacher.objects.create(
                        user=user,
                        department=request.POST.get('department', '')
                    )
                
                auth.login(request, user)
                return redirect('products:home')
        else:
            return render(request, 'accounts/signup.html', {'error': 'Passwords must match'})
    else:
        return render(request, 'accounts/signup.html')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid(): 
            user = form.get_user()
            auth.login(request, user)
            return redirect('products:home')
        else:
            return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('products:home')
    return redirect('products:home')