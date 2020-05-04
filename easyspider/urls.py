from django.urls import path

from easyspider import views

app_name = 'easyspider'
urlpatterns = [
    path('site-template/create/', views.create_site_template, name='site-template-create'),
    path('node/list/', views.NodeListView.as_view(), name='list-node'),
    path('node/modify/', views.modify_node, name='modify-node'),
    path('node/set-status/<int:node_id>/<int:status>/', views.set_node_status, name='set-node-status'),
    path('node/create/', views.create_node, name='create-node'),
    path('node/push/', views.push_node_template, name='push-node'),
]
