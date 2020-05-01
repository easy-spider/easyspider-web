from django.shortcuts import render


def data_download(request, task_pk):
    return render(request, 'task/dataDownload.html', {})


def my_task(request):
    return render(request, 'task/task.html', {})
