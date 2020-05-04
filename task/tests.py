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

    def test_set_name_invalid_length(self):
        """任务名称长度不在规定的范围内"""
        task = Task(user=self.user, template=self.template)
        for name in ('t1', ' t1 ', '     ', 't' * 30):
            with self.assertRaises(ValueError) as cm:
                task.set_name(name)
            self.assertEqual('任务名长度应在3~20之间', cm.exception.args[0])

    def test_set_name(self):
        task = Task(user=self.user, template=self.template)
        task.set_name('  task1\t\r\n')
        self.assertEqual('task1', task.name)

    def test_set_args_no_template(self):
        """任务没有关联的模板"""
        task = Task.objects.create(user=self.user, name='task1')
        split_arg = task.set_args({'p1': 'abc', 'p2': '123'})
        self.assertIsNone(task.args)
        self.assertEqual({}, task.args_dict())
        self.assertIsNone(split_arg)

    def test_set_args(self):
        task = Task.objects.create(user=self.user, template=self.template, name='task1')
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
        data = {'inputTaskName': 'task1', 'p1': 'abc', 'p2': '42'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertRedirects(response, reverse('login'))

    def test_404(self):
        """模板id不存在"""
        self.client.post(reverse('login'), {'username': 'zzy', 'password': '123456'})
        data = {'inputTaskName': 'task1', 'p1': 'abc', 'p2': '42'}
        response = self.client.post(reverse('create_task', args=(9999,)), data)
        self.assertEqual(404, response.status_code)

    def test_invalid_name_length(self):
        """任务名称长度不在规定的范围内"""
        self.client.post(reverse('login'), {'username': 'zzy', 'password': '123456'})
        data = {'p1': 'abc', 'p2': '42'}
        for name in ('t1', ' t1 ', '     ', 't' * 30):
            data['inputTaskName'] = name
            response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
            self.assertEqual({'status': 'ERROR', 'message': '任务名长度应在3~20之间'}, response.json())

    def test_name_already_exists(self):
        """任务名称已存在"""
        self.client.post(reverse('login'), {'username': 'zzy', 'password': '123456'})
        data = {'inputTaskName': 'task1', 'p1': 'abc', 'p2': '42'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'SUCCESS'}, response.json())
        data['inputTaskName'] = ' task1\t\r\n'
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'ERROR', 'message': '任务名称已存在'}, response.json())

    def test_split_arg_invalid(self):
        """划分参数的值不在规定的范围内"""
        self.client.post(reverse('login'), {'username': 'zzy', 'password': '123456'})
        data = {'inputTaskName': 'task1', 'p1': 'abc'}
        for p2 in (-5, 0, 100, 9999):
            data['p2'] = p2
            response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
            self.assertEqual(
                {'status': 'ERROR', 'message': '错误的值：{}，请输入1~99'.format(p2)},
                response.json()
            )

    def test_ok(self):
        """成功创建task和job"""
        self.client.post(reverse('login'), {'username': 'zzy', 'password': '123456'})
        data = {'inputTaskName': 'task1', 'p1': 'abc', 'p2': '18'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'SUCCESS'}, response.json())

        task = Task.objects.filter(user=self.user, template=self.template).first()
        self.assertEqual('task1', task.name)
        jobs = task.job_set.all()
        self.assertEqual({'abc'}, {json.loads(j.args)['p1'] for j in jobs})
        self.assertEqual(set(range(1, 19)), {json.loads(j.args)['p2'] for j in jobs})
