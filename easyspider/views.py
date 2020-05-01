from enum import IntEnum

import requests
from django.forms import model_to_dict
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.views import generic
from django.views.decorators.http import require_http_methods

from easyspider.models import Task, Node, Job
from spiderTemplate.models import Site


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
        # TODO: 增加task的Model中的“已中止”状态
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
    if get_client_ip(request) == '127.0.0.1' or \
            'username' in request.session and request.session['username'] == 'admin':
        node = get_object_or_404(Node, pk=node_id)
        if status not in [NodeStatus.ONLINE, NodeStatus.OFFLINE, NodeStatus.DISABLED]:
            return HttpResponseBadRequest()
        node.status = status
        node.save()
        return JsonResponse({'result': 'ok'})
    else:
        return HttpResponseForbidden()


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
            'project_name': job.task.template.site_templates.project_name,
            'spider_name': job.task.template.spider_name,
            'settings': job.task.template.site_templates.settings,
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
        if task.status == 'ready':
            task.status = 'running'
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
            task.status = 'finished'
            task.save()

    return JsonResponse({'result': 'ok'})


def set_job_node(request, job_id, node_id):
    """设置作业节点"""
    if get_client_ip(request) != '127.0.0.1':
        return HttpResponseForbidden()
    job = get_object_or_404(Job, pk=job_id)
    node = get_object_or_404(Node, pk=node_id)
    job.node_id = node.id
    job.save()
    return JsonResponse({'result': 'ok'})


class NodeListView(generic.ListView):
    model = Node
    template_name = 'easyspider/node.html'
    context_object_name = 'node_list'

    def dispatch(self, request, *args, **kwargs):
        if 'username' not in request.session:
            return HttpResponseForbidden('you have not logged in')
        if request.session['username'] != 'admin':
            return HttpResponseForbidden('you are not admin')
        return super(NodeListView, self).dispatch(request, *args, **kwargs)


@require_http_methods(['POST'])
def modify_node(request):
    """修改节点信息"""
    if 'username' not in request.session:
        return HttpResponseForbidden('you have not logged in')
    if request.session['username'] != 'admin':
        return HttpResponseForbidden('you are not admin')
    node = get_object_or_404(Node, pk=request.POST['id'])
    node.ip = request.POST['ip']
    node.port = request.POST['port']
    node.username = request.POST['username']
    node.password = request.POST['password']
    node.save()
    return JsonResponse({'result': 'ok'})


@require_http_methods(['POST'])
def create_node(request):
    """创建新节点"""
    if 'username' not in request.session:
        return HttpResponseForbidden('you have not logged in')
    if request.session['username'] != 'admin':
        return HttpResponseForbidden('you are not admin')
    Node.objects.create(
        ip=request.POST['ip'],
        port=request.POST['port'],
        username=request.POST['username'],
        password=request.POST['password'], status=NodeStatus.DISABLED)
    return JsonResponse({'result': 'ok'})


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
    if 'username' not in request.session:
        return HttpResponseForbidden('you have not logged in')
    if request.session['username'] != 'admin':
        return HttpResponseForbidden('you are not admin')
    templates = Site.objects.all()
    for template in templates:
        push_template(template.name, template.egg)
    return JsonResponse({'result': 'ok'})


def create_site_template(request):
    if 'username' not in request.session:
        return HttpResponseForbidden('you have not logged in')
    if request.session['username'] != 'admin':
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
        return JsonResponse({'result': 'ok'})
    return render(request, 'easyspider/site-template-create.html')
