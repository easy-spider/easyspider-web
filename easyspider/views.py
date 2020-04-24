import json
from enum import IntEnum

from django.forms import model_to_dict
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.views import generic
from django.views.decorators.http import require_http_methods

from easyspider.models import User, Template, Task, Node, Job


def index(request):
    """网站首页"""
    return render(request, 'easyspider/index.html', {'message': request.GET.get('message')})


@require_http_methods(['GET', 'POST'])
def register(request):
    """GET方法——注册页面；POST方法——提交注册表单"""
    if request.method == 'GET':
        return render(request, 'easyspider/register.html')
    username = request.POST['username']
    password = User.encrypt_password(request.POST['password'])
    if User.objects.filter(username=username).exists():
        return render(request, 'easyspider/register.html', {'error_message': '用户名已存在'})
    User.objects.create(username=username, password=password)
    return HttpResponseRedirect(reverse('easyspider:index') + '?message=注册成功')


@require_http_methods(['GET', 'POST'])
def login(request):
    """GET方法——登录页面；POST方法——提交登录表单"""
    if request.method == 'GET':
        return render(request, 'easyspider/login.html')
    username = request.POST['username']
    password = User.encrypt_password(request.POST['password'])
    try:
        user = User.objects.get(username=username)
        if user.password == password:
            request.session['username'] = user.username
            return redirect('easyspider:index')
        else:
            return render(request, 'easyspider/login.html', {'error_message': '用户名或密码错误'})
    except User.DoesNotExist:
        return render(request, 'easyspider/login.html', {'error_message': '用户名或密码错误'})


def logout(request):
    """用户注销"""
    if 'username' in request.session:
        del request.session['username']
    return HttpResponseRedirect(reverse('easyspider:index') + '?message=注销成功')


class TemplateListView(generic.ListView):
    """爬虫模板列表"""
    model = Template
    template_name = 'easyspider/template-list.html'
    context_object_name = 'template_list'


class TemplateDetailView(generic.DetailView):
    """爬虫模板详细信息"""
    model = Template
    template_name = 'easyspider/template-detail.html'


@require_http_methods(['POST'])
def create_task(request):
    """提交创建爬虫任务表单"""
    user = User.objects.get(username=request.session['username'])
    template = Template.objects.get(pk=request.POST['template_id'])
    args = {param: request.POST[param] for param in template.param_list()}
    Task.objects.create(user=user, template=template, name=request.POST['name'],
                        args=json.dumps(args, ensure_ascii=False), status='ready')
    return redirect(reverse('easyspider:index') + '?message=创建爬虫任务成功')


class TaskListView(generic.ListView):
    """爬虫任务列表"""
    model = Task
    template_name = 'easyspider/task-list.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        user = User.objects.get(username=self.request.session['username'])
        # user.task_set
        return Task.objects.filter(user=user).order_by('-create_time')


def change_task_status(request, task_id, status):
    """修改任务状态"""
    task = get_object_or_404(Task, pk=task_id)
    if task.user.username != request.session['username']:
        return HttpResponseForbidden('Not your task')
    task.status = status
    task.save()
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
    if get_client_ip(request) != '127.0.0.1':
        return HttpResponseForbidden()
    node = get_object_or_404(Node, pk=node_id)
    if status not in [NodeStatus.ONLINE, NodeStatus.OFFLINE, NodeStatus.DISABLED]:
        return HttpResponseBadRequest()
    node.status = status
    node.save()
    return JsonResponse({"result": "ok"})


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
    if status == JobStatus.FINISHED:
        # check other jobs with the same task
        other_jobs = get_list_or_404(Job, task_id=task.id)
        all_finished = True
        for j in other_jobs:
            if j.status != JobStatus.FINISHED:
                all_finished = False
                break
        # if all finished, mark the task finished
        if all_finished:
            task.status = "finished"
            task.save()
    return JsonResponse({"result": "ok"})


def set_job_node(request, job_id, node_id):
    """设置作业节点"""
    if get_client_ip(request) != '127.0.0.1':
        return HttpResponseForbidden()
    job = get_object_or_404(Job, pk=job_id)
    node = get_object_or_404(Node, pk=node_id)
    job.node_id = node.id
    job.save()
    return JsonResponse({"result": "ok"})
