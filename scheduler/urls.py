from django.urls import path

from scheduler import views

app_name = 'scheduler'
urlpatterns = [
    path('node/list-online/', views.list_online_node, name='list-online-node'),
    path('node/get/<int:node_id>/', views.get_node_by_id, name='get-node-by-id'),
    path('node/set-status/<int:node_id>/<int:status>/', views.set_node_status, name='set-node-status'),
    path('job/list/<int:status>/', views.list_job_by_status, name='job-list-by-status'),
    path('job/set-status/<str:job_id>/<int:status>/', views.set_job_status, name='set-job-status'),
    path('job/set-node/<str:job_id>/<int:node_id>/', views.set_job_node, name='set-job-node'),
]
