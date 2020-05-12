from datetime import datetime

from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import utc

from spiderTemplate.models import Site, SiteType, Template
from task.models import Task


def starter(request):
    """登录之后的起始页，展示8个网站模板集合"""
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    sites = Site.objects.all()[:8]
    return render(request, 'spiderTemplate/starter.html', {'sites': sites})


def sites_view(request):
    """网站模板集合列表

    GET参数：\n
    type - 按网站类型筛选，为空或"all"表示全部\n
    order - 排序规则，"update_time"表示按更新时间排序，为空或"hot"表示按总浏览次数排序\n
    search - 搜索关键词（此时type无效），为空表示全部
    """
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    order = request.GET.get('order', 'hot')
    sites = list(Site.objects.all())
    if order == 'update_time':
        sites.sort(key=lambda s: s.update_time or datetime.min.replace(tzinfo=utc), reverse=True)
    elif order == 'hot':
        view_times = {s.id: s.template_set.aggregate(n=Sum('view_times'))['n'] or 0 for s in sites}
        sites.sort(key=lambda s: view_times[s.id], reverse=True)

    keyword = request.GET.get('search', '')
    if keyword:
        sites = [s for s in sites if keyword.lower() in s.display_name.lower()]
        site_type = ''
    else:
        site_type = request.GET.get('type', 'all')
        if site_type and site_type != 'all':
            sites = [s for s in sites if s.site_type.name == site_type]

    context = {
        'site_types': SiteType.objects.all(),
        'type': site_type,
        'search': keyword,
        'order': order,
        'sites': sites
    }
    return render(request, 'spiderTemplate/templateFirst.html', context)


def templates_view(request, pk):
    """同一个集合的模板列表"""
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    site = Site.objects.get(pk=pk)
    context = {
        'site_name': site.display_name,
        'template_list': site.template_set.all().order_by('-view_times')
    }
    return render(request, 'spiderTemplate/templateSecond.html', context)


def template_info(request, pk):
    """模板详细信息"""
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    template = Template.objects.get(pk=pk)
    if not request.COOKIES.get('template_%s_view' % pk):
        template.view_times += 1
        template.save()
    context = {'template': Template.objects.get(pk=pk)}
    response = render(request, 'spiderTemplate/templateInfo.html', context)
    response.set_cookie('template_%s_view' % pk, 'true', max_age=60)
    return response


def template_setting(request, pk):
    """模板参数配置

    如果有GET参数taskID则表示重新编辑任务；否则表示初次创建任务
    """
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    context = {'template': Template.objects.get(pk=pk)}
    if 'taskID' in request.GET:
        context['task'] = Task.objects.get(pk=int(request.GET['taskID']))
    return render(request, 'spiderTemplate/templateSetting.html', context)
