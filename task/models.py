import json
from datetime import timedelta

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
    template = models.ForeignKey(Template, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)  # 最近编辑时间
    finish_time = models.DateTimeField(null=True, blank=True)
    args = models.CharField(max_length=4095, null=True)  # JSON格式的模板参数
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ready')
    run_times = models.IntegerField(default=1)  # 运行次数

    def __str__(self):
        return self.name

    def set_name(self, name):
        """设置任务名称，删除首尾空白符

        验证：检查长度在3~20个字符之间；同一个用户关联的任务名称没有重复

        :exception ValueError: 如果名称长度不在规定的范围内；或同任务名称已存在
        """
        name = name.strip()
        if not 3 <= len(name) <= 20:
            raise ValueError('任务名长度应在3~20个字符之间')
        elif self.user.task_set.exclude(pk=self.id).filter(name=name).exists():
            raise ValueError('任务名称已存在')
        self.name = name

    def set_args(self, arg_dict):
        """设置任务的模板参数

        :param arg_dict: {'param_name': 'value_str'}
        :return: 模板划分参数的值
        :exception ValueError: 如果参数值超过范围（数字类型）或长度超过限制（字符串类型）
        """
        template_params = {p.name: p for p in self.template.param_set.all()}
        args = {}
        split_arg = 1
        for param_name in arg_dict:
            if param_name not in template_params:
                continue
            param = template_params[param_name]
            if param.input_label == 'textarea' or param.input_type == 'text':
                v = arg_dict[param_name]
                if len(v) > param.length_limit:
                    raise ValueError('{}的长度不能超过{}'.format(
                        param.display_name, param.length_limit
                    ))
                args[param_name] = v
            elif param.input_type == 'number':
                v = int(arg_dict[param_name])
                if not param.number_min <= v <= param.number_max:
                    raise ValueError('{}的值应在{}~{}之间'.format(
                        param.display_name, param.number_min, param.number_max
                    ))
                args[param_name] = v
                if param.name == self.template.split_param:
                    split_arg = v
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
        if self.job_set.exists():
            return '{:.0%}'.format(self.job_set.filter(status=3).count() / self.job_set.count())
        else:
            return '0%'

    def duration(self):
        """以字符串形式返回运行耗时，未完成的返回空字符串"""
        if self.finish_time:
            d = self.finish_time - self.create_time
            return str(timedelta(seconds=int(d.total_seconds())))
        else:
            return ''
