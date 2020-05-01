import json

from django.contrib.auth.models import User
from django.db import models

from spiderTemplate.models import Template


class Node(models.Model):
    """Scrapyd节点实体类"""
    ip = models.CharField(max_length=50)
    port = models.IntegerField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    status = models.IntegerField(default=0, null=True)

    def __str__(self):
        return '{}:{}'.format(self.ip, self.port)


class Task(models.Model):
    """爬虫任务实体类"""
    STATUS_CHOICES = [
        ('ready', '等待运行'),
        ('running', '正在运行'),
        ('paused', '暂停运行'),
        ('finished', '完成运行')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    args = models.CharField(max_length=4095, null=True)  # JSON格式的模板参数
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return self.name

    def args_dict(self):
        """以字典形式返回模板参数"""
        return json.loads(self.args)


class Job(models.Model):
    """爬虫运行作业实体类"""
    STATUS_CHOICES = [
        (0, 'CREATED'),
        (1, 'PENDING'),
        (2, 'RUNNING'),
        (3, 'FINISHED')
    ]

    uuid = models.CharField(db_column='id', max_length=50, primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    node = models.ForeignKey(Node, on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    args = models.CharField(max_length=2047, null=True)  # JSON字符串序列化的参数

    def __str__(self):
        return self.uuid
