from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse('starter'))
    else:
        return render(request, 'index.html')


def get_recent_tasks(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "ERROR", "message": "未登录"})
    # 将top 5 task放入字典
    return JsonResponse({"status": "SUCCESS", "tasks": []})
