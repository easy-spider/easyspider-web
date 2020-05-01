from django.urls import path

from pic import views

app_name = 'pic'
urlpatterns = [
    path('site/logo/<str:name>/', views.site_logo, name='site-logo'),
    path(
        'template/logo/<str:site_name>/<str:template_name>/',
        views.template_logo, name='template-logo'
    ),
    path(
        'template/field/<str:site_name>/<str:template_name>/<str:field_name>/',
        views.template_field, name='template-field'
    ),
    path(
        'template/param/<str:site_name>/<str:template_name>/<str:param_name>/',
        views.template_param, name='template-param'
    ),
]
