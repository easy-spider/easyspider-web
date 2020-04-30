from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse


def starter(request):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        return render(request, 'spiderTemplate/starter.html', {})


def template_first(request):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        type = request.GET.get('type')
        order = request.GET.get('order')
        search_keyword = request.GET.get('search')
        # context = {}
        # context["type"] = "life"
        # context["order"] = 1
        # return render(request, 'spiderTemplate/templateFirst.html', context)
        return render(request, 'spiderTemplate/templateFirst.html', {})


def template_second(request, website):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        type = request.GET.get('type')
        order = request.GET.get('order')
        return render(request, 'spiderTemplate/templateSecond.html', {})


def template_info(request, website, subtemplate):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        return render(request, 'spiderTemplate/templateInfo.html', {})


def template_setting(request, website, subtemplate):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        # 查询数据库得到参数字段
        if request.method == "POST":
            # 后面需要写成循环的形式
            taskname = request.POST.get("inputTaskName", "")
            pagenum = request.POST.get("inputPageNum", "")
            url = request.POST.get("textareaUrl", "")
            # data validation, for example same task name...
            # according to Task model create a task instance & start a scrapy task
            # return jsonresponse
            data = {}
            data["status"] = "SUCCESS"
            return JsonResponse(data)
        else:
            return render(request, 'spiderTemplate/templateSetting.html', {})


def deal_setting_form(request):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    else:
        pass
