from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse

from task.models import Task


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse('starter'))
    else:
        return render(request, 'index.html')


def get_recent_tasks(request):
    """最近编辑任务Top 5"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'ERROR', 'message': '未登录'})
    recent_tasks = Task.objects.order_by('-create_time')[:5]
    return JsonResponse({
        'status': 'SUCCESS',
        'tasks': [{'id': t.id, 'name': t.name} for t in recent_tasks]
    })
