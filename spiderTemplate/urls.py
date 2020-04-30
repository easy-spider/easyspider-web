from django.urls import path
from . import views

urlpatterns = [
    path('', views.starter, name="starter"),
    path('template', views.template_first, name="template_first"),
    path('template/<str:website>', views.template_second, name="template_second"),
    path('template/<str:website>/<str:subtemplate>', views.template_info, name="template_info"),
    path('templateSetting/<str:website>/<str:subtemplate>', views.template_setting, name="template_setting")
]
