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
        return redirect(reverse('starter'))
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
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
    # User.first_name用于存储昵称
    nickname = request.POST['first_name']
    if User.objects.filter(username=username).exists():
        return render(request, 'user/register.html', {'error_message': '用户名已存在'})
    User.objects.create_user(username, email, password, first_name=nickname)
    return redirect(reverse('index'))


def send_reset_email(request):
    return render(request, 'user/send_reset_email.html', {})


def forgot_password(request):
    return render(request, 'user/forgot_password.html', {})


@require_http_methods(['GET', 'POST'])
def reset_password(request):
    if request.method == 'GET':
        return render(request, 'user/reset_password.html')
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    request.user.set_password(request.POST['password'])
    request.user.save()
    return redirect(reverse('user_profile'))


@require_http_methods(['GET', 'POST'])
def user_profile(request):
    """GET方法——个人信息页面；POST方法——修改个人信息"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    if request.method == 'GET':
        return render(request, 'user/information.html')
    request.user.email = request.POST['email']
    request.user.first_name = request.POST['first_name']
    request.user.save()
    return redirect(reverse('user_profile'))
