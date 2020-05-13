import logging
import os
import re
from enum import IntEnum

import requests
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from EasySpiderWeb import settings
from pic.views import save_pic
from scheduler.models import Node
from spiderTemplate.models import Site, Template, Field, Param

logger = logging.getLogger('administrator_view')


class NodeStatus(IntEnum):
    ONLINE = 0
    OFFLINE = 1
    DISABLED = 2


def list_node(request):
    """列出所有节点"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    return render(request, 'administrator/node.html', {'node_list': Node.objects.all()})


@require_http_methods(['POST'])
def modify_node(request):
    """修改节点信息"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    node = get_object_or_404(Node, pk=request.POST['id'])
    node.ip = request.POST['ip']
    node.port = request.POST['port']
    node.username = request.POST['username']
    node.password = request.POST['password']
    node.save()
    return redirect(reverse('list_node'))


@require_http_methods(['POST'])
def create_node(request):
    """创建新节点"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    Node.objects.create(
        ip=request.POST['ip'],
        port=request.POST['port'],
        username=request.POST['username'],
        password=request.POST['password'],
        status=NodeStatus.DISABLED
    )
    return redirect(reverse('list_node'))


def delete_node(request, pk):
    """删除节点"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    node = get_object_or_404(Node, pk=pk)
    node.delete()
    return HttpResponse(status=204)


def inspect_node(request, pk):
    """查看服务器运行状态"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    node = get_object_or_404(Node, pk=pk)
    try:
        url = f'http://{node.ip}:{node.port}/daemonstatus.json'
        r = requests.get(url, auth=(node.username, node.password)).json()
        return JsonResponse(r)
    except requests.exceptions.RequestException as _e:
        node.status = NodeStatus.OFFLINE
        node.save()
    return HttpResponseBadRequest()


def set_node_status(request, node_id, status):
    """设置节点状态"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    node = get_object_or_404(Node, pk=node_id)
    if status not in [NodeStatus.ONLINE, NodeStatus.OFFLINE, NodeStatus.DISABLED]:
        return HttpResponseBadRequest()
    node.status = status
    node.save()
    return HttpResponse(status=204)


def push_egg(project_name: str, egg_path: str):
    """
    向所有在线节点推送模板集合的Egg

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


def push_all_eggs(request):
    """推送所有模板集合的Egg到在线节点"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    for site in Site.objects.all():
        if not os.path.exists(site.egg):
            continue
        push_egg(site.name, site.egg)
    return HttpResponse(status=204)


def list_template(request):
    """列出所有模板"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    context = {'template_list': Template.objects.all()}
    return render(request, 'administrator/templateSearchAdmin.html', context)


@require_http_methods(['GET', 'POST'])
def create_template(request):
    """GET方法——创建模板页面；POST方法——提交创建模板表单"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    if request.method == 'GET':
        return render(request, 'administrator/templateUpload.html', {'site_list': Site.objects.all()})

    try:
        site_name = request.POST['site_name']
        site = Site.objects.get(name=site_name)
        template_name = request.POST['name']
        if site.template_set.filter(name=template_name).exists():
            raise ValueError('"{}"集合下模板名{}已存在'.format(site.display_name, template_name))

        # 保存模板信息
        template = Template.objects.create(
            site=site, name=template_name, display_name=request.POST['display_name'],
            introduction=request.POST['introduction'], split_param=request.POST['split_param'],
            update_time=timezone.now(), sample_data=request.POST['sample_data']
        )
        save_pic(request.FILES['logo'], os.path.join(site_name, template_name, 'logo.jpg'))

        # 保存采集字段
        field_name_pat = re.compile(r'field_name(\d+)')
        for k in request.POST:
            m = re.fullmatch(field_name_pat, k)
            if m:
                n = m.group(1)
                field_name = request.POST[k]
                Field.objects.create(
                    template=template, name=field_name,
                    display_name=request.POST['field_display_name' + n]
                )
                save_pic(
                    request.FILES['field_pic' + n],
                    os.path.join(site_name, template_name, 'field', field_name)
                )

        # 保存模板参数
        param_name_pat = re.compile(r'param_name(\d+)')
        for k in request.POST:
            m = re.fullmatch(param_name_pat, k)
            if m:
                n = m.group(1)
                param_name = request.POST[k]
                param = Param(
                    template=template, name=param_name,
                    display_name=request.POST['param_display_name' + n],
                    input_label=request.POST['param_input_label' + n],
                    input_type=request.POST['param_input_type' + n]
                )
                if param.input_label == 'textarea' or param.input_type == 'text':
                    param.length_limit = int(request.POST['param_length_limit' + n])
                elif param.input_type == 'number':
                    param.number_max = int(request.POST['param_number_max' + n])
                    param.number_min = int(request.POST['param_number_min' + n])
                param.save()
                save_pic(
                    request.FILES['param_pic' + n],
                    os.path.join(site_name, template_name, 'param', param_name)
                )

        # egg文件
        egg_path = f'egg/{site_name}.egg'
        upload_egg = request.FILES['egg']
        with open(egg_path, 'wb+') as local_egg:
            for chunk in upload_egg.chunks():
                local_egg.write(chunk)
        push_egg(site_name, egg_path)

        # 更新模板集合
        site.egg = egg_path
        site.update_time = timezone.now()
        site.save()
        return redirect(reverse('list_template'))
    except ValueError as e:
        context = {
            'site_list': Site.objects.all(),
            'error_message': e.args[0]
        }
        return render(request, 'administrator/templateUpload.html', context)


@require_http_methods(['GET', 'POST'])
def modify_template(request, pk):
    """GET方法——修改模板页面；POST方法——提交修改模板表单"""
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    template = get_object_or_404(Template, pk=pk)
    if request.method == 'GET':
        context = {'template': template}
        return render(request, 'administrator/templateModify.html', context)

    site = template.site
    # egg文件
    egg_path = f'egg/{site.name}.egg'
    upload_egg = request.FILES['egg']
    with open(egg_path, 'wb+') as local_egg:
        for chunk in upload_egg.chunks():
            local_egg.write(chunk)
    push_egg(site.name, egg_path)

    # 更新模板集合
    site.egg = egg_path
    site.update_time = timezone.now()
    site.save()
    return redirect(reverse('list_template'))


@require_http_methods(['POST'])
def delete_template(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden('you are not admin')
    pk = request.POST['delete_id']
    template = get_object_or_404(Template, pk=pk)
    if not template.can_delete():
        return HttpResponseForbidden('this template cannot be deleted now')
    try:
        client = MongoClient(settings.MONGODB_URI)
        client.drop_database('{}_{}'.format(template.site.name, template.name))
        client.close()
    except PyMongoError:
        logger.exception('MongoDB删除数据库失败')
    for task in template.task_set.all():
        task.job_set.all().delete()
        task.delete()
    template.delete()
    return redirect(reverse('list_template'))
