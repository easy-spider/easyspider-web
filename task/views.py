import json
import logging
import uuid

import requests
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from requests import RequestException

from EasySpiderWeb import settings
from scheduler.models import Job
from scheduler.views import JobStatus
from spiderTemplate.models import Template
from task.models import Task

logger = logging.getLogger('task_view')


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


def restart_task(request, task_pk):
    """提交重新运行任务表单"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = get_object_or_404(Task, pk=task_pk)
    if task.user_id != request.user.id:
        return HttpResponseForbidden('Not your task')
    if task.status not in ['finished', 'canceled']:
        return HttpResponseForbidden('Operation not allowed')

    template = task.template
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
        task.create_time = timezone.now()
        task.finish_time = None
        task.status = 'ready'
        task.run_times += 1
        task.save()
        task.job_set.all().delete()
        task_arg = task.args_dict()
        for i in range(split_arg):
            task_arg[template.split_param] = i + 1
            Job.objects.create(uuid=uuid.uuid4(), task=task, args=json.dumps(task_arg))
        recent_tasks = Task.objects.order_by('-create_time')[:5]
        return JsonResponse({
            'status': 'SUCCESS',
            'tasks': [{'id': t.id, 'name': t.name} for t in recent_tasks]
        })


def task_list(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
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


def cancel_job(job):
    """在节点上取消作业"""
    node = job.node
    if node is None:
        return
    url = f'http://{node.ip}:{node.port}/cancel.json'
    data = {'project': job.task.template.site.name, 'job': job.uuid}
    try:
        requests.post(url, data, auth=(node.username, node.password), timeout=3)
    except RequestException:
        logger.exception('节点%s取消作业失败', node)


# {current_status: [allowed_status]}
ALLOWED_OPERATION = {
    'ready': ['paused', 'canceled'],
    'running': ['paused', 'canceled'],
    'paused': ['running', 'canceled']
}


@require_http_methods(['POST'])
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
        for job in task.job_set.filter(status=JobStatus.PENDING):
            cancel_job(job)
            job.status = JobStatus.CREATED
            job.save()
    elif status == 'canceled':
        for job in task.job_set.exclude(status=JobStatus.FINISHED):
            cancel_job(job)
            job.status = JobStatus.FINISHED
            job.save()
    return JsonResponse({'status': 'SUCCESS'})


@require_http_methods(['POST'])
def clear_data(request, task_pk):
    """清除任务的爬取结果数据"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = get_object_or_404(Task, pk=task_pk)
    if task.user_id != request.user.id:
        return HttpResponseForbidden('Not your task')
    if task.status not in ['finished', 'canceled']:
        return HttpResponseForbidden('Operation not allowed')

    try:
        client = MongoClient(settings.MONGODB_URI)
        db = client['{}_{}'.format(task.template.site.name, task.template.name)]
        for job in task.job_set.all():
            db.drop_collection('{}_{}'.format(task.id, job.uuid))
        client.close()
        return JsonResponse({'status': 'SUCCESS'})
    except PyMongoError:
        logger.exception('MongoDB删除集合失败')
        return JsonResponse({'status': 'ERROR', 'message': '删除数据失败'})


@require_http_methods(['POST'])
def delete_task(request, task_pk):
    r = clear_data(request, task_pk)
    if isinstance(r, JsonResponse) and json.loads(r.content.decode())['status'] == 'SUCCESS':
        task = Task.objects.get(pk=task_pk)
        task.job_set.all().delete()
        task.delete()
    return r


@require_http_methods(['POST'])
def batch_delete_task(request):
    for i in json.loads(request.POST['ids']):
        r = delete_task(request, i)
        if not isinstance(r, JsonResponse) or json.loads(r.content.decode())['status'] != 'SUCCESS':
            return r
    return JsonResponse({'status': 'SUCCESS'})


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
        documents.extend(db['{}_{}'.format(task.id, job.uuid)].find(projection={'_id': False}))
    client.close()

    template_fields = list(task.template.field_set.all())
    field_list = [f.display_name for f in template_fields]
    sample_data = [[d[f.name] for f in template_fields] for d in documents[:15]]
    context = {
        'task_id': task.id, 'field_list': field_list,
        'sample_data': sample_data, 'full_data': documents
    }
    return render(request, 'task/dataDownload.html', context)


def download_data(request, task_pk):
    """用户点击下载数据按钮，更新模板的下载计数"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = get_object_or_404(Task, pk=task_pk)
    if task.user_id != request.user.id:
        return HttpResponseForbidden('Not your task')

    task.template.download_times += 1
    task.template.save()
    return JsonResponse({'status': 'SUCCESS'})
