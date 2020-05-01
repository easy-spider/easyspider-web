from django.contrib import admin

from spiderTemplate import models

admin.site.register(models.SiteType)
admin.site.register(models.Site)
admin.site.register(models.Template)
admin.site.register(models.Field)
admin.site.register(models.Param)
