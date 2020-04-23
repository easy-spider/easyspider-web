from django.contrib import admin

from easyspider.models import User, Template, Node, Task, Job

admin.site.register(User)
admin.site.register(Template)
admin.site.register(Node)
admin.site.register(Task)
admin.site.register(Job)
