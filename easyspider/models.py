import hashlib
import json

from django.db import models


class User(models.Model):
    """用户实体类"""
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=40)

    def __str__(self):
        return self.username

    @classmethod
    def encrypt_password(cls, password):
        """使用SHA-1加密密码，返回长度为40的加密后的字符串。"""
        return hashlib.sha1(password.encode()).hexdigest()


class SiteTemplates(models.Model):
    """同网站爬虫模板集合实体类，对应一个Scrapy项目。"""
    name = models.CharField(max_length=255)  # 模板集合名称（如“豆瓣”）
    project_name = models.CharField(max_length=255, unique=True)  # Scrapy项目名称
    egg = models.CharField(max_length=2047)  # Scrapy项目打包egg的路径
    settings = models.CharField(max_length=2047, blank=True, null=True)  # 传递给Scrapy的其他运行设置

    def __str__(self):
        return self.name


class Template(models.Model):
    """爬虫模板实体类，对应Scrapy项目中的一个Spider。"""
    site_templates = models.ForeignKey(SiteTemplates, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # 模板名称（如“豆瓣热门电影”）
    spider_name = models.CharField(max_length=255)  # 对应的Spider名字
    introduction = models.CharField(max_length=2047, null=True)
    params = models.CharField(max_length=255, null=True)  # ";"分隔的模板参数

    def __str__(self):
        return self.name

    def param_list(self):
        """以列表形式返回模板参数"""
        return self.params.split(';')


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
    node = models.ForeignKey(Node, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    args = models.CharField(max_length=2047, null=True)  # JSON字符串序列化的参数

    def __str__(self):
        return self.uuid
