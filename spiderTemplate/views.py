from django.shortcuts import render, redirect
from django.urls import reverse

from spiderTemplate.models import Site, SiteType, Template


def starter(request):
    """登录之后的起始页，展示8个网站模板集合"""
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    sites = Site.objects.all()[:8]
    return render(request, 'spiderTemplate/starter.html', {'sites': sites})


def sites_view(request):
    """网站模板集合列表

    GET参数：\n
    type - 按网站类型筛选，为空表示“热门”\n
    order - 排序规则，"update_time"表示按更新时间排序，为空表示“热门”，
    网站的更新时间为其关联的所有模板中最新的更新时间\n
    search - 搜索关键词（此时type无效），为空表示全部
    """
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    order = request.GET.get('order', 'hot')
    sites = list(Site.objects.all().order_by('-update_time')) if order == 'update_time' \
        else list(Site.objects.all())

    keyword = request.GET.get('search', '')
    if keyword:
        sites = [s for s in sites if keyword.lower() in s.display_name.lower()]
        site_type = ''
    else:
        site_type = request.GET.get('type', 'hot')
        if site_type and site_type != 'hot':
            sites = [s for s in sites if s.site_type.name == site_type]
        else:
            sites = sites[:8]

    context = {
        'site_types': SiteType.objects.all(),
        'type': site_type,
        'search': keyword,
        'order': order,
        'sites': sites
    }
    return render(request, 'spiderTemplate/templateFirst.html', context)


def templates_view(request, pk):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    site = Site.objects.get(pk=pk)
    context = {
        'site_name': site.display_name,
        'template_list': site.template_set.all()
    }
    return render(request, 'spiderTemplate/templateSecond.html', context)


def template_info(request, pk):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    context = {'template': Template.objects.get(pk=pk)}
    return render(request, 'spiderTemplate/templateInfo.html', context)


def template_setting(request, pk):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    context = {'template': Template.objects.get(pk=pk)}
    return render(request, 'spiderTemplate/templateSetting.html', context)
