from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/task/(?P<user_pk>\w+)/$', consumers.TaskConsumer),
]
