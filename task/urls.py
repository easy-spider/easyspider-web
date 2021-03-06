from django.urls import path

from . import views

urlpatterns = [
    path('', views.task_list, name='my_task'),
    path('recentTasks/', views.recent_tasks_view, name="get_recent_tasks"),
    path('create/<int:template_pk>/', views.create_task, name='create_task'),
    path('restart/<int:task_pk>/', views.restart_task, name='restart_task'),

    path('rename/<int:task_pk>/', views.rename_task, name='rename_task'),
    path('pause/<int:task_pk>/', views.change_task_status,
         {'status': 'paused'}, name='pause_task'),
    path('resume/<int:task_pk>/', views.change_task_status,
         {'status': 'running'}, name='resume_task'),
    path('cancel/<int:task_pk>/', views.change_task_status,
         {'status': 'canceled'}, name='cancel_task'),
    path('delete/<int:task_pk>/', views.delete_task, name='delete_task'),
    path('batchDelete/', views.batch_delete_task, name='batch_delete_task'),

    path('clearData/<int:task_pk>/', views.clear_data, name='clear_data'),
    path('previewData/<int:task_pk>/', views.preview_data, name='preview_data'),
    path('getSpiderData/<int:task_pk>/', views.get_spider_data, name='get_spider_data'),
    path('downloadData/<int:task_pk>/', views.download_data, name='download_data'),
]
