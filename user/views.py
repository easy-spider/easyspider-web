from django.shortcuts import render


def login(request):
    return render(request, 'user/login.html', {})


def send_reset_email(request):
    return render(request, 'user/email.html', {})


def forget_password(request):
    return render(request, 'user/forgot_password.html', {})


def register(request):
    return render(request, 'user/register.html', {})


def reset_password(request):
    return render(request, 'user/reset_password.html', {})


def user_profile(request):
    return render(request, 'user/information.html', {})
