from django.db import models

from task.models import Task


class Node(models.Model):
    """Scrapyd节点实体类"""
    ip = models.CharField(max_length=50)
    port = models.IntegerField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    status = models.IntegerField(default=0, null=True)

    def __str__(self):
        return '{}:{}'.format(self.ip, self.port)


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
    args = models.CharField(max_length=4095, null=True)  # JSON字符串序列化的参数

    def __str__(self):
        return self.uuid
