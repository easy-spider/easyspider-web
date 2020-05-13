from django.urls import path

from easyspider import views

urlpatterns = [
    path('node/list/', views.list_node, name='list_node'),
    path('node/modify/', views.modify_node, name='modify_node'),
    path('node/create/', views.create_node, name='create_node'),
    path('node/delete/<int:pk>/', views.delete_node, name='delete_node'),
    path('node/inspect/<int:pk>/', views.inspect_node, name='inspect_node'),
    path('node/set-status/<int:node_id>/<int:status>/', views.set_node_status, name='set-node-status'),
    path('node/push/', views.push_all_eggs, name='push_eggs'),
    path('template/list/', views.list_template, name='list_template'),
    path('template/create/', views.create_template, name='create_template'),
    path('template/modify/<int:pk>/', views.modify_template, name='modify_template'),
    path('template/delete/', views.delete_template, name='delete_template'),
]
