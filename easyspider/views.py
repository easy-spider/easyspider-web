from enum import IntEnum

import requests
from django.contrib.auth import get_user
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.decorators.http import require_http_methods

from scheduler.models import Job, Node
from spiderTemplate.models import Site
from task.models import Task


def change_task_status(request, task_id, status):
    """修改任务状态"""
    task = get_object_or_404(Task, pk=task_id)
    if task.user.username != request.session['username']:
        return HttpResponseForbidden('Not your task')
    task.status = status
    task.save()
    if status == 'paused':
        jobs = Job.objects.filter(task_id=task.id)
        for job in jobs:
            if job.status is JobStatus.PENDING:
                node = job.node
                url = f'http://{node.ip}:{node.port}/cancel.json'
                data = {
                    'project': job.task.template.site_templates.project_name,
                    'job': job.uuid
                }
                requests.post(url, data, auth=(node.username, node.password), timeout=3)
                job.status = JobStatus.CREATED
                job.save()
    elif status == 'canceled':
        jobs = Job.objects.filter(task_id=task.id)
        for job in jobs:
            if job.status in [JobStatus.CREATED, JobStatus.PENDING, JobStatus.RUNNING]:
                node = job.node
                url = f'http://{node.ip}:{node.port}/cancel.json'
                data = {
                    'project': job.task.template.site_templates.project_name,
                    'job': job.uuid
                }
                requests.post(url, data, auth=(node.username, node.password), timeout=3)
                job.status = JobStatus.FINISHED
                job.save()
    return redirect(reverse('easyspider:task-list'))


class JobStatus(IntEnum):
    CREATED = 0
    PENDING = 1
    RUNNING = 2
    FINISHED = 3


class NodeStatus(IntEnum):
    ONLINE = 0
    OFFLINE = 1
    DISABLED = 2


class NodeListView(generic.ListView):
    model = Node
    template_name = 'easyspider/node.html'
    context_object_name = 'node_list'

    def dispatch(self, request, *args, **kwargs):
        if not get_user(request).is_superuser:
            return HttpResponseForbidden('you are not admin')
        return super(NodeListView, self).dispatch(request, *args, **kwargs)


@require_http_methods(['POST'])
def modify_node(request):
    """修改节点信息"""
    if not get_user(request).is_superuser:
        return HttpResponseForbidden('you are not admin')
    node = get_object_or_404(Node, pk=request.POST['id'])
    node.ip = request.POST['ip']
    node.port = request.POST['port']
    node.username = request.POST['username']
    node.password = request.POST['password']
    node.save()
    return HttpResponse(status=204)


def set_node_status(request, node_id, status):
    """设置节点状态"""
    if not get_user(request).is_superuser:
        return HttpResponseForbidden('you are not admin')
    node = get_object_or_404(Node, pk=node_id)
    if status not in [NodeStatus.ONLINE, NodeStatus.OFFLINE, NodeStatus.DISABLED]:
        return HttpResponseBadRequest()
    node.status = status
    node.save()
    return HttpResponse(status=204)


@require_http_methods(['POST'])
def create_node(request):
    """创建新节点"""
    if not get_user(request).is_superuser:
        return HttpResponseForbidden('you are not admin')
    Node.objects.create(
        ip=request.POST['ip'],
        port=request.POST['port'],
        username=request.POST['username'],
        password=request.POST['password'], status=NodeStatus.DISABLED)
    return HttpResponse(status=204)


def push_template(project_name: str, egg_path: str):
    """
    向所有在线节点推送模板的Egg

    :param project_name: template name to be deployed
    :param egg_path: absolute path to egg file on this machine
    """
    nodes = Node.objects.filter(status=NodeStatus.ONLINE)
    for node in nodes:
        try:
            url = f'http://{node.ip}:{node.port}/delproject.json'
            data = {'project': project_name}
            requests.post(url, data=data, auth=(node.username, node.password), timeout=3)
            url = f'http://{node.ip}:{node.port}/addversion.json'
            data = {'project': project_name, 'version': 'r1'}
            requests.post(url, files={'egg': open(egg_path, 'rb')}, data=data, auth=(
                node.username, node.password))
        except requests.exceptions.RequestException as _e:
            node.status = NodeStatus.OFFLINE
            node.save()


def push_node_template(request):
    """推送模板Egg到Scraypd节点"""
    if not get_user(request).is_superuser:
        return HttpResponseForbidden('you are not admin')
    templates = Site.objects.all()
    for template in templates:
        push_template(template.name, template.egg)
    return HttpResponse(status=204)


def create_site_template(request):
    if not get_user(request).is_superuser:
        return HttpResponseForbidden('you are not admin')
    if request.method == 'POST':
        project_name = request.POST['project_name']
        egg_path = f'egg/{project_name}.egg'
        f = request.FILES['egg']
        with open(egg_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        Site.objects.create(
            name=project_name,
            display_name=request.POST['name'],
            egg=egg_path,
            settings=request.POST['settings']
            # TODO: 添加其他字段
        )
        # 推送Egg文件
        push_template(project_name, egg_path)
        return HttpResponse(status=204)
    return render(request, 'easyspider/site-template-create.html')
