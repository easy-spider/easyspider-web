import os

from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound

from EasySpiderWeb import settings

PIC_DIR = os.path.join(settings.BASE_DIR, 'upload', 'templatepics')


def read_pic(rel_path):
    """从PIC_DIR下读取图片，返回HttpResponse对象。

    :param rel_path: PIC_DIR下的相对路径
    :return: 200 - 正常读取；404 - 文件不存在；403 - 文件位置超出范围
    """
    path = os.path.abspath(os.path.join(PIC_DIR, rel_path))
    if not path.startswith(PIC_DIR):
        return HttpResponseForbidden()
    try:
        with open(path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/jpeg')
    except FileNotFoundError:
        return HttpResponseNotFound()


def save_pic(pic_file, dst_path):
    """将图片保存到PIC_DIR目录，不存在的目录将被自动创建

    :param pic_file: 图片文件对象
    :param dst_path: 目标文件在PIC_DIR下的相对路径
    :exception ValueError: 如果文件位置超出范围
    """
    path = os.path.abspath(os.path.join(PIC_DIR, dst_path))
    if not path.startswith(PIC_DIR):
        raise ValueError('dst out of directory')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        for chunk in pic_file.chunks():
            f.write(chunk)


def site_logo(request, name):
    """网站图标"""
    return read_pic(os.path.join(name, 'logo.jpg'))


def template_logo(request, site_name, template_name):
    """模板图标"""
    return read_pic(os.path.join(site_name, template_name, 'logo.jpg'))


def template_field(request, site_name, template_name, field_name):
    """采集字段预览图片"""
    return read_pic(os.path.join(site_name, template_name, 'field', field_name + '.jpg'))


def template_param(request, site_name, template_name, param_name):
    """模板参数预览图片"""
    return read_pic(os.path.join(site_name, template_name, 'param', param_name + '.jpg'))
