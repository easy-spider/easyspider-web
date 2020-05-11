from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from spiderTemplate.models import Site, Template, Field, Param, SiteType


class SiteModelTests(TestCase):

    def test_logo(self):
        """网站图标URL"""
        site = Site(name='site1', display_name='site1', egg='')
        self.assertEqual('/pic/site/logo/site1/', site.logo())


class TemplateModelTests(TestCase):

    def test_logo(self):
        """模板图标URL"""
        site = Site(name='site1', display_name='site1', egg='')
        template = Template(
            site=site, name='template1', display_name='template1',
            introduction='', split_param='', sample_data=''
        )
        self.assertEqual('/pic/template/logo/site1/template1/', template.logo())


class FieldModelTests(TestCase):

    def test_pic(self):
        """采集字段预览图片URL"""
        site = Site(name='site1', display_name='site1', egg='')
        template = Template(
            site=site, name='template1', display_name='template1',
            introduction='', split_param='', sample_data=''
        )
        field = Field(template=template, name='field1', display_name='field1')
        self.assertEqual('/pic/template/field/site1/template1/field1/', field.pic())


class ParamModelTests(TestCase):

    def test_pic(self):
        """模板参数预览图片URL"""
        site = Site(name='site1', display_name='site1', egg='')
        template = Template(
            site=site, name='template1', display_name='template1',
            introduction='', split_param='', sample_data=''
        )
        param = Param(template=template, name='param1', display_name='field1')
        self.assertEqual('/pic/template/param/site1/template1/param1/', param.pic())


def create_test_data():
    User.objects.create_user(username='zzy', password='123456', email='zzy@example.com')
    site_types = [SiteType.objects.create(name=t, display_name=t) for t in 'ABC']
    for i in range(1, 11):
        site_name = 'S{}'.format(i)
        site = Site.objects.create(
            name=site_name, display_name=site_name, site_type=site_types[(i - 1) % 3],
            egg='', update_time=datetime(2020, 5, i)
        )
        for j in range(1, 4):
            template_name = 'T{},{}'.format(i, j)
            Template.objects.create(
                site=site, name=template_name, display_name=template_name,
                introduction='', split_param='', sample_data='', view_times=(10 - i) * 10 + j
            )


class StarterViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_data()

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        response = self.client.get(reverse('starter'))
        self.assertRedirects(response, reverse('login'))

    def test_logged_in(self):
        """已登录时访问index重定向到starter"""
        self.client.login(username='zzy', password='123456')
        response = self.client.get(reverse('index'), follow=True)
        self.assertRedirects(response, reverse('starter'))
        self.assertQuerysetEqual(
            response.context['sites'],
            ['<Site: S{}>'.format(i) for i in range(1, 9)],
            ordered=False
        )


class SitesViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_data()

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        response = self.client.get(reverse('template_first'))
        self.assertRedirects(response, reverse('login'))

    def test_no_args(self):
        """无参数跳转到该页面"""
        self.client.login(username='zzy', password='123456')
        response = self.client.get(reverse('template_first'))
        self.assertEqual('all', response.context['type'])
        self.assertEqual('', response.context['search'])
        self.assertEqual('hot', response.context['order'])
        self.assertEqual(
            ['S{}'.format(i) for i in range(1, 11)],
            [str(s) for s in response.context['sites']]
        )

    def test_search(self):
        """按网站名称搜索，只有search参数"""
        self.client.login(username='zzy', password='123456')
        response = self.client.get(reverse('template_first') + '?search=S1')
        self.assertEqual('', response.context['type'])
        self.assertEqual('S1', response.context['search'])
        self.assertEqual('hot', response.context['order'])
        self.assertEqual(['S1', 'S10'], [str(s) for s in response.context['sites']])

    def test_search_order_update_time(self):
        """按网站名称搜索，search+order参数，order=update_time"""
        self.client.login(username='zzy', password='123456')
        response = self.client.get(reverse('template_first') + '?search=S1&order=update_time')
        self.assertEqual('', response.context['type'])
        self.assertEqual('S1', response.context['search'])
        self.assertEqual('update_time', response.context['order'])
        self.assertEqual(['S10', 'S1'], [str(s) for s in response.context['sites']])

    def test_type_order_hot(self):
        """按类型筛选，type+order参数，order=hot"""
        self.client.login(username='zzy', password='123456')
        response = self.client.get(reverse('template_first') + '?type=A&order=hot')
        self.assertEqual('A', response.context['type'])
        self.assertEqual('', response.context['search'])
        self.assertEqual('hot', response.context['order'])
        self.assertEqual(['S1', 'S4', 'S7', 'S10'], [str(s) for s in response.context['sites']])

    def test_type_order_update_time(self):
        """按类型筛选，type+order参数，order=update_time"""
        self.client.login(username='zzy', password='123456')
        response = self.client.get(reverse('template_first') + '?type=B&order=update_time')
        self.assertEqual('B', response.context['type'])
        self.assertEqual('', response.context['search'])
        self.assertEqual('update_time', response.context['order'])
        self.assertEqual(['S8', 'S5', 'S2'], [str(s) for s in response.context['sites']])


class TemplatesViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_data()

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        response = self.client.get(reverse('template_second', args=(1,)))
        self.assertRedirects(response, reverse('login'))

    def test_ok(self):
        """正常访问"""
        self.client.login(username='zzy', password='123456')
        site = Site.objects.get(name='S1')
        response = self.client.get(reverse('template_second', args=(site.id,)))
        self.assertEqual('S1', response.context['site_name'])
        self.assertQuerysetEqual(
            response.context['template_list'],
            ['<Template: T1,3>', '<Template: T1,2>', '<Template: T1,1>'],
            ordered=False
        )
