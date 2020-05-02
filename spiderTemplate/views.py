from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse

from spiderTemplate.models import Site, SiteType, Template


def starter(request):
    """登录之后的起始页，展示8个网站模板集合"""
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        sites = Site.objects.all()[:8]
        return render(request, 'spiderTemplate/starter.html', {'sites': sites})


def sites_view(request):
    """网站模板集合列表

    GET参数：\n
    type - 按网站类型筛选，为空表示“热门”\n
    order - 排序规则，"update_time"表示按更新时间排序，为空表示“热门”，
    网站的更新时间为其关联的所有模板中最新的更新时间\n
    search - 搜索关键词，为空表示全部
    """
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        sites = Site.objects.all()

        site_type = request.GET.get('type')
        if site_type:
            sites = sites.filter(site_type__name=site_type)
        else:
            sites = sites[:8]
            site_type = 'hot'

        keyword = request.GET.get('search')
        if keyword:
            sites = sites.filter(display_name__contains=keyword)

        order = request.GET.get('order')
        if order == 'update_time':
            sites.order_by('-update_time')
        else:
            order = 'hot'

        context = {
            'site_types': SiteType.objects.all(),
            'type': site_type,
            'order': order,
            'sites': sites,
        }
        return render(request, 'spiderTemplate/templateFirst.html', context)


def templates_view(request, pk):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        context = {'template_list': Site.objects.get(pk=pk).template_set}
        return render(request, 'spiderTemplate/templateSecond.html', context)


def template_info(request, pk):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        context = {'template': Template.objects.get(pk=pk)}
        return render(request, 'spiderTemplate/templateInfo.html', context)


def template_setting(request, pk):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        if request.method == 'POST':
            task_name = request.POST.get('inputTaskName', '')
            args = {}
            template = Template.objects.get(pk=pk)
            for param in template.param_set:
                args[param.name] = request.POST[param.name]
            # data validation, for example same task name...
            # according to Task model create a task instance & start a scrapy task
            # return jsonresponse
            # 成功：{'status': 'SUCCESS'}
            # 失败：{'status': 'ERROR', 'message': message中文}
            # 创建task
            return JsonResponse({'status': 'SUCCESS'})
        else:
            context = {'template': Template.objects.get(pk=pk)}
            return render(request, 'spiderTemplate/templateSetting.html', context)
