from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login as auth_login

def home(request):
    return render(request, 'accounts/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('accounts:home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def logout(request):
    return render(request, 'accounts/home.html')
