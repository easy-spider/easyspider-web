from django.urls import path

from . import views

urlpatterns = [
    path('create/<int:template_pk>/', views.create_task, name='create_task'),
    path('', views.my_task, name="my_task"),
    path('rename/<int:task_pk>/', views.rename_task, name='rename_task'),
    path('delete/<int:task_pk>/', views.delete_task, name='delete_task'),
    path('clearData/<int:task_pk>/', views.clear_data, name='clear_data'),
    path('dataDownload/<int:task_pk>/', views.data_download, name="data_download"),
]
