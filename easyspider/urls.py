from django.urls import path

from easyspider import views

app_name = 'easyspider'
urlpatterns = [
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('template/list/', views.TemplateListView.as_view(), name='template-list'),
    path('template/detail/<int:pk>/', views.TemplateDetailView.as_view(), name='template-detail'),

    path('task/create/', views.create_task, name='create-task'),
    path('task/list/', views.TaskListView.as_view(), name='task-list'),
    path('task/start/<int:task_id>/', views.change_task_status,
         {'status': 'running'}, name='start-task'),
    path('task/pause/<int:task_id>/', views.change_task_status,
         {'status': 'paused'}, name='pause-task'),
    path('task/stop/<int:task_id>/', views.change_task_status,
         {'status': 'finished'}, name='stop-task'),
]
