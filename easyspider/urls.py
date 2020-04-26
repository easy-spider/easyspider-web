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
    path('site-template/create/', views.create_site_template, name='site-template-create'),
    path('task/create/', views.create_task, name='create-task'),
    path('task/list/', views.TaskListView.as_view(), name='task-list'),
    path('task/start/<int:task_id>/', views.change_task_status,
         {'status': 'running'}, name='start-task'),
    path('task/pause/<int:task_id>/', views.change_task_status,
         {'status': 'paused'}, name='pause-task'),
    path('task/stop/<int:task_id>/', views.change_task_status,
         {'status': 'finished'}, name='stop-task'),
    path('node/list/', views.NodeListView.as_view(), name='list-node'),
    path('node/modify/', views.modify_node, name='modify-node'),
    path('node/create/', views.create_node, name='create-node'),
    path('node/push/', views.push_node_template, name='push-node'),
    path('node/list-online/', views.list_online_node, name='list-online-node'),
    path('node/get/<int:node_id>/', views.get_node_by_id, name='get-node-by-id'),
    path('node/set-status/<int:node_id>/<int:status>/', views.set_node_status, name='set-node-status'),
    path('job/list/<int:status>/', views.list_job_by_status, name='job-list-by-status'),
    path('job/set-status/<str:job_id>/<int:status>/', views.set_job_status, name='set-job-status'),
    path('job/set-node/<str:job_id>/<int:node_id>/', views.set_job_node, name='set-job-node'),
]
