import json
import uuid

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from scheduler.models import Job
from spiderTemplate.models import Template
from task.models import Task


@require_http_methods(['POST'])
def create_task(request, template_pk):
    """提交创建任务表单"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    else:
        template = get_object_or_404(Template, pk=template_pk)
        task = Task(user=request.user, template=template, name=request.POST['inputTaskName'])
        split_arg = task.set_args(
            {param.name: request.POST[param.name] for param in template.param_set.all()}
        )
        if split_arg <= 0:
            return JsonResponse(
                {'status': 'ERROR', 'message': '错误的值：{}，请输入1~100'.format(split_arg)},
                json_dumps_params={'ensure_ascii': False}
            )
        elif split_arg > 100:
            return JsonResponse(
                {'status': 'ERROR', 'message': '值过大：{}，请输入1~100'.format(split_arg)},
                json_dumps_params={'ensure_ascii': False}
            )
        else:
            task.save()
            task_arg = task.args_dict()
            for i in range(split_arg):
                task_arg[template.split_param] = i + 1
                Job.objects.create(uuid=uuid.uuid4(), task=task, args=json.dumps(task_arg))
            return JsonResponse({'status': 'SUCCESS'})


def data_download(request, task_pk):
    return render(request, 'task/dataDownload.html', {})


def my_task(request):
    return render(request, 'task/task.html', {})
