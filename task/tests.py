import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from spiderTemplate.models import Site, Template, Param
from task.models import Task


def create_test_data():
    user = User.objects.create_user(username='zzy', password='123456', email='')
    site = Site.objects.create(name='S1', display_name='S1', egg='')
    template = Template.objects.create(
        site=site, name='T1', display_name='T1',
        introduction='', split_param='p2', sample_data=''
    )
    Param.objects.create(template=template, name='p1', display_name='p1', input_type='text')
    Param.objects.create(template=template, name='p2', display_name='p2', input_type='number')
    return user, template


class TaskModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user, cls.template = create_test_data()

    def test_set_args_no_template(self):
        """任务没有关联的模板"""
        task = Task.objects.create(user=self.user, name='t1')
        split_arg = task.set_args({'p1': 'abc', 'p2': '123'})
        self.assertIsNone(task.args)
        self.assertEqual({}, task.args_dict())
        self.assertIsNone(split_arg)

    def test_set_args(self):
        task = Task.objects.create(user=self.user, template=self.template, name='t1')
        split_arg = task.set_args({'p1': 'abc', 'p2': '123', 'p3': 'what'})
        self.assertEqual('{"p1": "abc", "p2": 123}', task.args)
        self.assertEqual({'p1': 'abc', 'p2': 123}, task.args_dict())
        self.assertEqual(123, split_arg)


class CreateTaskViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user, cls.template = create_test_data()

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        data = {'inputTaskName': 't1', 'p1': 'abc', 'p2': '42'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertRedirects(response, reverse('login'))

    def test_404(self):
        """模板id不存在"""
        self.client.post(reverse('login'), {'username': 'zzy', 'password': '123456'})
        data = {'inputTaskName': 't1', 'p1': 'abc', 'p2': '42'}
        response = self.client.post(reverse('create_task', args=(9999,)), data)
        self.assertEqual(404, response.status_code)

    def test_split_arg_non_positive(self):
        """划分参数的值为非正"""
        self.client.post(reverse('login'), {'username': 'zzy', 'password': '123456'})
        data = {'inputTaskName': 't1', 'p1': 'abc', 'p2': '-5'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'ERROR', 'message': '错误的值：-5，请输入1~100'}, response.json())
        data = {'inputTaskName': 't1', 'p1': 'abc', 'p2': '0'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'ERROR', 'message': '错误的值：0，请输入1~100'}, response.json())

    def test_split_arg_too_large(self):
        """划分参数的值过大"""
        self.client.post(reverse('login'), {'username': 'zzy', 'password': '123456'})
        data = {'inputTaskName': 't1', 'p1': 'abc', 'p2': '1234'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'ERROR', 'message': '值过大：1234，请输入1~100'}, response.json())

    def test_ok(self):
        """成功创建task和job"""
        self.client.post(reverse('login'), {'username': 'zzy', 'password': '123456'})
        data = {'inputTaskName': 't1', 'p1': 'abc', 'p2': '18'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'SUCCESS'}, response.json())

        task = Task.objects.filter(user=self.user, template=self.template).first()
        self.assertEqual('t1', task.name)
        jobs = task.job_set.all()
        self.assertEqual({'abc'}, {json.loads(j.args)['p1'] for j in jobs})
        self.assertEqual(set(range(1, 19)), {json.loads(j.args)['p2'] for j in jobs})
