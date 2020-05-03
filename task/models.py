import json

from django.contrib.auth.models import User
from django.db import models

from spiderTemplate.models import Template


class Task(models.Model):
    """爬虫任务实体类"""
    STATUS_CHOICES = [
        ('ready', '等待运行'),
        ('running', '正在运行'),
        ('paused', '暂停运行'),
        ('finished', '完成运行'),
        ('canceled', '已终止')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField(null=True, blank=True)
    args = models.CharField(max_length=4095, null=True)  # JSON格式的模板参数
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ready')

    def __str__(self):
        return self.name

    def args_dict(self):
        """以字典形式返回模板参数"""
        return json.loads(self.args)
