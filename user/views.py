from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """GET方法——登录页面；POST方法——提交登录表单"""
    if request.method == 'GET':
        return render(request, 'user/login.html')
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # TODO 重定向到spiderTemplate:starter
        return redirect(reverse(''))
    else:
        return render(request, 'user/login.html', {'error_message': '用户名或密码错误'})


def logout_view(request):
    """用户注销"""
    logout(request)
    return redirect(reverse('index'))


@require_http_methods(['GET', 'POST'])
def register(request):
    """GET方法——注册页面；POST方法——提交注册表单"""
    if request.method == 'GET':
        return render(request, 'user/register.html')
    # TODO 注册需要提交的信息：用户名？、密码、邮箱
    username = request.POST['username']
    password = request.POST['password']
    if User.objects.filter(username=username).exists():
        return render(request, 'user/register.html', {'error_message': '用户名已存在'})
    User.objects.create(username=username, password=password)
    return redirect(reverse('index'))


def send_reset_email(request):
    return render(request, 'user/send_reset_email.html', {})


def forgot_password(request):
    return render(request, 'user/forgot_password.html', {})


def reset_password(request):
    return render(request, 'user/reset_password.html', {})


def user_profile(request):
    return render(request, 'user/information.html', {})
