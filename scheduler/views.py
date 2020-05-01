from enum import IntEnum, Enum

from django.forms import model_to_dict
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, get_list_or_404

from easyspider.models import Node, Job, Task


class JobStatus(IntEnum):
    CREATED = 0
    PENDING = 1
    RUNNING = 2
    FINISHED = 3


class NodeStatus(IntEnum):
    ONLINE = 0
    OFFLINE = 1
    DISABLED = 2


class TaskStatus(Enum):
    READY = 'ready'
    RUNNING = 'running'
    PAUSED = 'paused'
    FINISHED = 'finished'
    CANCELED = 'canceled'


def get_client_ip(request):
    """获取请求客户端的IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def list_online_node(request):
    """列出在线节点"""
    if get_client_ip(request) != '127.0.0.1':
        return HttpResponseForbidden()
    result = list(Node.objects.filter(status=NodeStatus.ONLINE).values())
    return JsonResponse(result, safe=False)


def get_node_by_id(request, node_id):
    """通过节点ID取得节点信息"""
    if get_client_ip(request) != '127.0.0.1':
        return HttpResponseForbidden()
    node = model_to_dict(get_object_or_404(Node, pk=node_id))
    return JsonResponse(node)


def set_node_status(request, node_id, status):
    """设置节点状态"""
    if get_client_ip(request) != '127.0.0.1':
        return HttpResponseForbidden()
    node = get_object_or_404(Node, pk=node_id)
    if status not in [NodeStatus.ONLINE, NodeStatus.OFFLINE, NodeStatus.DISABLED]:
        return HttpResponseBadRequest()
    node.status = status
    node.save()
    return HttpResponse(status=204)


def list_job_by_status(request, status):
    """列出处于某状态的作业"""
    if get_client_ip(request) != '127.0.0.1':
        return HttpResponseForbidden()
    if status not in [JobStatus.CREATED, JobStatus.PENDING, JobStatus.RUNNING, JobStatus.FINISHED]:
        return HttpResponseBadRequest()
    qs = Job.objects.filter(status=status)
    result = []
    for job in qs:
        result.append({
            'id': job.uuid,
            'project_name': job.task.template.site.name,
            'spider_name': job.task.template.name,
            'settings': job.task.template.site.settings,
            'args': job.args,
            'node_id': job.node.id,
            'status': job.status,
            'task_status': job.task.status,
            'task_id': job.task.id
        })
    return JsonResponse(result, safe=False)


def set_job_status(request, job_id, status):
    """设置作业状态"""
    if get_client_ip(request) != '127.0.0.1':
        return HttpResponseForbidden()
    job = get_object_or_404(Job, pk=job_id)
    if status not in [JobStatus.CREATED, JobStatus.PENDING, JobStatus.RUNNING, JobStatus.FINISHED]:
        return HttpResponseBadRequest()
    job.status = status
    job.save()
    task = get_object_or_404(Task, pk=job.task_id)
    if status == JobStatus.RUNNING:
        if task.status == TaskStatus.READY:
            task.status = TaskStatus.RUNNING
            task.save()
    elif status == JobStatus.FINISHED:
        # check other jobs with the same task
        other_jobs = get_list_or_404(Job, task_id=task.id)
        all_finished = True
        for j in other_jobs:
            if j.status != JobStatus.FINISHED:
                all_finished = False
                break
        # if all finished, mark the task finished
        if all_finished:
            task.status = TaskStatus.FINISHED
            task.save()
    return HttpResponse(status=204)


def set_job_node(request, job_id, node_id):
    """设置作业节点"""
    if get_client_ip(request) != '127.0.0.1':
        return HttpResponseForbidden()
    job = get_object_or_404(Job, pk=job_id)
    node = get_object_or_404(Node, pk=node_id)
    job.node_id = node.id
    job.save()
    return HttpResponse(status=204)
