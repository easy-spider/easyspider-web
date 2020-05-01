from django.urls import path
from . import views

urlpatterns = [
    path('dataDownload/<int:task_pk>', views.data_download, name="data_download"),
    path('', views.my_task, name="my_task"),
]
