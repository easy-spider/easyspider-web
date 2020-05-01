from django.contrib import admin

from spiderTemplate import models

admin.site.register(models.Site)
admin.site.register(models.Template)
admin.site.register(models.Field)
admin.site.register(models.InputType)
admin.site.register(models.Param)
