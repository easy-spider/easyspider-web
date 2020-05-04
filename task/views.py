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
        task = Task(user=request.user, template=template)
        try:
            task.set_name(request.POST['inputTaskName'])
        except ValueError as e:
            return JsonResponse(
                {'status': 'ERROR', 'message': e.args[0]},
                json_dumps_params={'ensure_ascii': False}
            )
        if request.user.task_set.filter(name=task.name):
            return JsonResponse(
                {'status': 'ERROR', 'message': '任务名称已存在'},
                json_dumps_params={'ensure_ascii': False}
            )

        split_arg = task.set_args(
            {param.name: request.POST[param.name] for param in template.param_set.all()}
        )
        if not 1 <= split_arg <= 99:
            return JsonResponse(
                {'status': 'ERROR', 'message': '错误的值：{}，请输入1~99'.format(split_arg)},
                json_dumps_params={'ensure_ascii': False}
            )
        else:
            task.save()
            task_arg = task.args_dict()
            for i in range(split_arg):
                task_arg[template.split_param] = i + 1
                Job.objects.create(uuid=uuid.uuid4(), task=task, args=json.dumps(task_arg))
            return JsonResponse({'status': 'SUCCESS'})


def my_task(request):
    context = {'task_list': request.user.task_set.all()}
    return render(request, 'task/task.html', context)


@require_http_methods(['POST'])
def rename_task(request, task_pk):
    return redirect(reverse('my_task'))


def delete_task(request, task_pk):
    # 删除task, job, mongodb
    return redirect(reverse('my_task'))


def clear_data(request, task_pk):
    return redirect(reverse('data_download'))


def data_download(request, task_pk):
    return render(request, 'task/dataDownload.html', {})
