import json
import uuid

import requests
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from pymongo import MongoClient

from EasySpiderWeb import settings
from scheduler.models import Job
from spiderTemplate.models import Template
from task.models import Task


@require_http_methods(['POST'])
def create_task(request, template_pk):
    """提交创建任务表单"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    template = get_object_or_404(Template, pk=template_pk)
    task = Task(user=request.user, template=template)
    try:
        task.set_name(request.POST['inputTaskName'])
    except ValueError as e:
        return JsonResponse(
            {'status': 'ERROR', 'message': e.args[0]},
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


def task_list(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    if request.method == "POST":
        print(request.POST.get("id"))
        # 根据for参数编写不同后端逻辑
        return JsonResponse({"status": "SUCCESS"})
    context = {'task_list': request.user.task_set.all()}
    return render(request, 'task/task.html', context)


@require_http_methods(['POST'])
def rename_task(request, task_pk):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = get_object_or_404(Task, pk=task_pk)
    if task.user_id != request.user.id:
        return HttpResponseForbidden('Not your task')
    try:
        task.set_name(request.POST['inputTaskName'])
        task.save()
        return JsonResponse({'status': 'SUCCESS'})
    except ValueError as e:
        return JsonResponse(
            {'status': 'ERROR', 'message': e.args[0]},
            json_dumps_params={'ensure_ascii': False}
        )


# {current_status: [allowed_status]}
ALLOWED_OPERATION = {
    'ready': ['paused', 'canceled'],
    'running': ['paused', 'canceled'],
    'paused': ['running', 'canceled']
}


def change_task_status(request, task_pk, status):
    """修改任务状态"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = get_object_or_404(Task, pk=task_pk)
    if task.user_id != request.user.id:
        return HttpResponseForbidden('Not your task')
    if task.status not in ALLOWED_OPERATION or status not in ALLOWED_OPERATION[task.status]:
        return HttpResponseForbidden('Operation not allowed')

    task.status = status
    task.save()
    if status == 'paused':
        for job in task.job_set.filter(status='PENDING'):
            node = job.node
            url = f'http://{node.ip}:{node.port}/cancel.json'
            data = {
                'project': job.task.template.site.name,
                'job': job.uuid
            }
            requests.post(url, data, auth=(node.username, node.password), timeout=3)
            job.status = 'CREATED'
            job.save()
    elif status == 'canceled':
        for job in task.job_set.filter(status__in=['CREATED', 'PENDING', 'RUNNING']):
            node = job.node
            url = f'http://{node.ip}:{node.port}/cancel.json'
            data = {
                'project': job.task.template.site.name,
                'job': job.uuid
            }
            requests.post(url, data, auth=(node.username, node.password), timeout=3)
            job.status = 'FINISHED'
            job.save()
    return redirect(reverse('my_task'))


def delete_task(request, task_pk):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = get_object_or_404(Task, pk=task_pk)
    if task.user_id != request.user.id:
        return HttpResponseForbidden('Not your task')
    if task.status not in ['finished', 'canceled']:
        return HttpResponseForbidden('Operation not allowed')

    client = MongoClient(settings.MONGODB_URI)
    db = client['{}_{}'.format(task.template.site.name, task.template.name)]
    for job in task.job_set.all():
        db.drop_collection('{}_{}'.format(task.id, job.uuid))
    client.close()

    task.job_set.all().delete()
    task.delete()
    return redirect(reverse('my_task'))


def clear_data(request, task_pk):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = get_object_or_404(Task, pk=task_pk)
    if task.user_id != request.user.id:
        return HttpResponseForbidden('Not your task')
    if task.status not in ['finished', 'canceled']:
        return HttpResponseForbidden('Operation not allowed')

    client = MongoClient(settings.MONGODB_URI)
    db = client['{}_{}'.format(task.template.site.name, task.template.name)]
    for job in task.job_set.all():
        db.drop_collection('{}_{}'.format(task.id, job.uuid))
    client.close()
    return redirect(reverse('preview_data', args=(task_pk,)))


# def preview_data(request, task_pk):
#     if not request.user.is_authenticated:
#         return redirect(reverse('login'))
#     if request.method == "POST":
#         # 根据for参数编写不同后端逻辑
#         return JsonResponse({"status": "SUCCESS"})
#     # get中也包含参数，关于download的
#     return render(request, 'task/dataDownload.html', {})


def preview_data(request, task_pk):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = get_object_or_404(Task, pk=task_pk)
    if task.user_id != request.user.id:
        return HttpResponseForbidden('Not your task')

    client = MongoClient(settings.MONGODB_URI)
    db = client['{}_{}'.format(task.template.site.name, task.template.name)]
    documents = []
    for job in task.job_set.all():
        if len(documents) >= 15:
            break
        documents.extend(db['{}_{}'.format(task.id, job.uuid)].find())
    client.close()

    template_fields = list(task.template.field_set.all())
    field_list = [f.display_name for f in template_fields]
    sample_data = [[d[f.name] for f in template_fields] for d in documents[:15]]
    context = {'field_list': field_list, 'sample_data': sample_data}
    return render(request, 'task/dataDownload.html', context)


def download_data(request, task_pk):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = get_object_or_404(Task, pk=task_pk)
    if task.user_id != request.user.id:
        return HttpResponseForbidden('Not your task')
    if task.status not in ['finished', 'canceled']:
        return HttpResponseForbidden('Operation not allowed')

    client = MongoClient(settings.MONGODB_URI)
    db = client['{}_{}'.format(task.template.site.name, task.template.name)]
    documents = []
    for job in task.job_set.all():
        documents.extend(db['{}_{}'.format(task.id, job.uuid)].find(projection={'_id': False}))
    client.close()
    return JsonResponse({'data': documents}, json_dumps_params={'ensure_ascii': False})
