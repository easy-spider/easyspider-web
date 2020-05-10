from django.urls import path

from easyspider import views

urlpatterns = [
    path('node/list/', views.list_node, name='list_node'),
    path('node/modify/<int:pk>/', views.modify_node, name='modify_node'),
    path('node/create/', views.create_node, name='create_node'),
    path('pushEggs/', views.push_all_eggs, name='push_eggs'),
    path('template/list/', views.list_template, name='list_template'),
    path('template/create/', views.create_template, name='create_template'),
]
