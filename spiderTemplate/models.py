from django.db import models
from django.urls import reverse


class SiteType(models.Model):
    """网站类型实体类"""
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)

    def __str__(self):
        return self.display_name


class Site(models.Model):
    """同网站爬虫模板集合实体类，对应一个Scrapy项目"""
    name = models.CharField(max_length=255, unique=True)  # 网站英文名（如"douban"），对应Scrapy项目名称
    display_name = models.CharField(max_length=255)  # 展示名称（如“豆瓣”）
    site_type = models.ForeignKey(SiteType, on_delete=models.SET_NULL, null=True)
    egg = models.CharField(max_length=2047)  # Scrapy项目打包egg的路径
    settings = models.CharField(max_length=2047, blank=True, null=True)  # 传递给Scrapy的其他运行设置
    update_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.display_name

    def logo(self):
        return reverse('pic:site-logo', args=(self.name,))


class Template(models.Model):
    """爬虫模板实体类，对应Scrapy项目中的一个Spider"""
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # 模板英文名（如"movie"），对应Spider名字
    display_name = models.CharField(max_length=255)  # 展示名称（如“豆瓣热门电影”）
    introduction = models.TextField()  # 模板简介（HTML格式）
    split_param = models.CharField(max_length=255)  # 用哪个参数划分任务
    update_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    sample_data = models.TextField()  # 示例数据（HTML格式）
    view_times = models.IntegerField(default=0)  # 浏览次数
    download_times = models.IntegerField(default=0)  # 关联的任务下载数据次数

    def __str__(self):
        return self.display_name

    def logo(self):
        return reverse('pic:template-logo', args=(self.site.name, self.name))

    def can_delete(self):
        return not self.task_set.exclude(status__in=['finished', 'canceled']).exists()


class Field(models.Model):
    """采集字段实体类"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # 字段英文名（如"rating"），对应预览图片文件名
    display_name = models.CharField(max_length=255)  # 展示名称（如“评分”）

    def __str__(self):
        return '{} - {}'.format(self.template, self.display_name)

    def pic(self):
        """预览图片URL"""
        return reverse('pic:template-field', args=(
            self.template.site.name, self.template.name, self.name
        ))


class Param(models.Model):
    """模板参数实体类"""
    INPUT_LABEL_CHOICES = [
        ('input', 'input'),
        ('textarea', 'textarea')
    ]

    INPUT_TYPE_CHOICES = [
        ('text', 'text'),
        ('number', 'number')
    ]

    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # 参数英文名（如"name"），对应预览图片文件名
    display_name = models.CharField(max_length=255)  # 展示名称（如“电影名称”）
    input_label = models.CharField(max_length=255, choices=INPUT_LABEL_CHOICES, default='input')
    input_type = models.CharField(max_length=255, choices=INPUT_TYPE_CHOICES, default='text')
    number_min = models.IntegerField(default=1)  # input_type==number时的最小值
    number_max = models.IntegerField(default=99)  # input_type==number时的最大值
    length_limit = models.IntegerField(default=255)  # input_type==text时的长度限制

    def __str__(self):
        return '{} - {}'.format(self.template, self.display_name)

    def pic(self):
        return reverse('pic:template-param', args=(
            self.template.site.name, self.template.name, self.name
        ))
