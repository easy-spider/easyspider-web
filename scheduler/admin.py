from django.contrib import admin

from scheduler import models

admin.site.register(models.Node)
admin.site.register(models.Job)
