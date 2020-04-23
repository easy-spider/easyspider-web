import json

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.decorators.http import require_http_methods

from easyspider.models import User, Template, Task


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
