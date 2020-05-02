from django.urls import path

from . import views

urlpatterns = [
    path('', views.starter, name="starter"),
    path('sites/', views.sites_view, name="template_first"),
    path('templates/<int:pk>/', views.templates_view, name="template_second"),
    path('templateInfo/<int:pk>/', views.template_info, name="template_info"),
    path('templateSetting/<int:pk>/', views.template_setting, name="template_setting")
]
