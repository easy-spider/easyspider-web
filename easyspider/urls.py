from django.urls import path

from easyspider import views

app_name = 'easyspider'
urlpatterns = [
    path('site-template/create/', views.create_site_template, name='site-template-create'),
    path('task/start/<int:task_id>/', views.change_task_status,
         {'status': 'running'}, name='start-task'),
    path('task/pause/<int:task_id>/', views.change_task_status,
         {'status': 'paused'}, name='pause-task'),
    path('task/stop/<int:task_id>/', views.change_task_status,
         {'status': 'finished'}, name='stop-task'),
    path('node/list/', views.NodeListView.as_view(), name='list-node'),
    path('node/modify/', views.modify_node, name='modify-node'),
    path('node/set-status/<int:node_id>/<int:status>/', views.set_node_status, name='set-node-status'),
    path('node/create/', views.create_node, name='create-node'),
    path('node/push/', views.push_node_template, name='push-node'),
]
