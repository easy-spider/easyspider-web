import json

from django.contrib.auth.models import User
from django.db import models

from spiderTemplate.models import Template


class Task(models.Model):
    """爬虫任务实体类"""
    STATUS_CHOICES = [
        ('ready', '等待运行'),
        ('running', '正在运行'),
        ('paused', '已暂停'),
        ('finished', '已完成'),
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

    def set_name(self, name):
        """设置任务名称，删除首尾空白符

        验证：检查长度在3~20之间；同一个用户关联的任务名称没有重复

        :exception ValueError: 如果名称长度不在规定的范围内；或同任务名称已存在
        """
        name = name.strip()
        if not 3 <= len(name) <= 20:
            raise ValueError('任务名长度应在3~20个字符之间')
        elif self.user.task_set.filter(name=name).exists():
            raise ValueError('任务名称已存在')
        self.name = name

    def set_args(self, arg_dict):
        """设置任务的模板参数

        :param arg_dict: {'param_name': 'value_str'}
        :return: 划分参数的值；如果没有关联的模板则返回None
        """
        if not self.template:
            return None
        template_params = {p.name: p for p in self.template.param_set.all()}
        args = {}
        split_arg = None
        for param_name in arg_dict:
            if param_name not in template_params:
                continue
            param = template_params[param_name]
            if param.input_label == 'textarea' or param.input_type == 'text':
                args[param_name] = arg_dict[param_name]
            elif param.input_type == 'number':
                split_arg = args[param_name] = int(arg_dict[param_name])
        self.args = json.dumps(args, ensure_ascii=False)
        return split_arg

    def args_dict(self):
        """以字典形式返回模板参数"""
        return json.loads(self.args) if self.args else {}

    def display_status(self):
        for s in self.STATUS_CHOICES:
            if s[0] == self.status:
                return s[1]

    def progress(self):
        """以字符串形式返回完成进度百分比（如"70%"）"""
        return '{:.0%}'.format(self.job_set.filter(status=3).count() / self.job_set.count())
