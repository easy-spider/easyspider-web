from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:template_pk>/', views.create_task, name='create_task'),
    path('dataDownload/<int:task_pk>/', views.data_download, name="data_download"),
    path('', views.my_task, name="my_task"),
]
