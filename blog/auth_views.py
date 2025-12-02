from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def custom_login(request):
    if request.user.is_authenticated:
        # Redirect based on user role
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.is_staff:
            return redirect('user_dashboard')
        else:
            return redirect('post_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user role
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.is_staff:
                return redirect('user_dashboard')
            else:
                return redirect('post_list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'blog/login.html')

def custom_logout(request):
    logout(request)
    return redirect('custom_login')
