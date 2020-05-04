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

    def test_name_already_exists(self):
        """任务名称已存在"""
        Task.objects.create(user=self.user, template=self.template, name='task1')
        task = Task(user=self.user, template=self.template)
        with self.assertRaises(ValueError) as cm:
            task.set_name(' task1\t\r\n')
        self.assertEqual('任务名称已存在', cm.exception.args[0])

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
        self.client.login(username='zzy', password='123456')
        data = {'inputTaskName': 'task1', 'p1': 'abc', 'p2': '42'}
        response = self.client.post(reverse('create_task', args=(9999,)), data)
        self.assertEqual(404, response.status_code)

    def test_invalid_name_length(self):
        """任务名称长度不在规定的范围内"""
        self.client.login(username='zzy', password='123456')
        data = {'p1': 'abc', 'p2': '42'}
        for name in ('t1', ' t1 ', '     ', 't' * 30):
            data['inputTaskName'] = name
            response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
            self.assertEqual({'status': 'ERROR', 'message': '任务名长度应在3~20之间'}, response.json())

    def test_name_already_exists(self):
        """任务名称已存在"""
        self.client.login(username='zzy', password='123456')
        Task.objects.create(user=self.user, template=self.template, name='task1')
        data = {'inputTaskName': ' task1\t\r\n', 'p1': 'abc', 'p2': '42'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'ERROR', 'message': '任务名称已存在'}, response.json())

    def test_split_arg_invalid(self):
        """划分参数的值不在规定的范围内"""
        self.client.login(username='zzy', password='123456')
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
        self.client.login(username='zzy', password='123456')
        data = {'inputTaskName': 'task1', 'p1': 'abc', 'p2': '18'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'SUCCESS'}, response.json())

        task = Task.objects.filter(user=self.user, template=self.template).first()
        self.assertEqual('task1', task.name)
        jobs = task.job_set.all()
        self.assertEqual({'abc'}, {json.loads(j.args)['p1'] for j in jobs})
        self.assertEqual(set(range(1, 19)), {json.loads(j.args)['p2'] for j in jobs})


class TaskListViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        for username in ('foo', 'bar'):
            user = User.objects.create_user(username=username, password='123456', email='')
            for i in range(1, 3):
                Task.objects.create(user=user, name='{}_task{}'.format(username, i))

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        response = self.client.get(reverse('my_task'))
        self.assertRedirects(response, reverse('login'))

    def test_ok(self):
        self.client.login(username='foo', password='123456')
        response = self.client.get(reverse('my_task'))
        self.assertQuerysetEqual(
            response.context['task_list'],
            ['<Task: foo_task1>', '<Task: foo_task2>'],
            ordered=False
        )


class RenameTaskViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.foo = User.objects.create_user(username='foo', password='123456', email='')
        cls.foo_task = Task.objects.create(user=cls.foo, name='foo_task1')
        Task.objects.create(user=cls.foo, name='foo_task2')
        cls.bar = User.objects.create_user(username='bar', password='123456', email='')
        cls.bar_task = Task.objects.create(user=cls.bar, name='bar_task1')

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        data = {'inputTaskName': 'foo_task2'}
        response = self.client.post(reverse('rename_task', args=(self.foo_task.id,)), data)
        self.assertRedirects(response, reverse('login'))

    def test_not_found(self):
        """任务id不存在"""
        self.client.login(username='foo', password='123456')
        data = {'inputTaskName': 'foo_task2'}
        response = self.client.post(reverse('rename_task', args=(9999,)), data)
        self.assertEqual(404, response.status_code)

    def test_forbidden(self):
        """任务id不属于当前用户"""
        self.client.login(username='foo', password='123456')
        data = {'inputTaskName': 'foo_task2'}
        response = self.client.post(reverse('rename_task', args=(self.bar_task.id,)), data)
        self.assertEqual(403, response.status_code)
        self.assertEqual(b'Not your task', response.content)

    def test_invalid_name_length(self):
        """任务名称长度不在规定的范围内"""
        self.client.login(username='foo', password='123456')
        for name in ('t1', ' t1 ', '     ', 't' * 30):
            data = {'inputTaskName': name}
            response = self.client.post(reverse('rename_task', args=(self.foo_task.id,)), data)
            self.assertEqual({'status': 'ERROR', 'message': '任务名长度应在3~20之间'}, response.json())

    def test_name_already_exists(self):
        """任务名称已存在"""
        self.client.login(username='foo', password='123456')
        data = {'inputTaskName': 'foo_task2'}
        response = self.client.post(reverse('rename_task', args=(self.foo_task.id,)), data)
        self.assertEqual({'status': 'ERROR', 'message': '任务名称已存在'}, response.json())

    def test_ok(self):
        self.client.login(username='foo', password='123456')
        data = {'inputTaskName': ' foo_task3\t\r\n'}
        response = self.client.post(reverse('rename_task', args=(self.foo_task.id,)), data)
        self.assertEqual({'status': 'SUCCESS'}, response.json())
        self.assertEqual('foo_task3', Task.objects.get(pk=self.foo_task.id).name)


class ChangeTaskStatusViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='zzy', password='123456', email='')
        cls.ready_task = Task.objects.create(user=cls.user, name='task1', status='ready')
        cls.running_task = Task.objects.create(user=cls.user, name='task2', status='running')
        cls.paused_task = Task.objects.create(user=cls.user, name='task3', status='paused')
        cls.finished_task = Task.objects.create(user=cls.user, name='task4', status='finished')
        cls.canceled_task = Task.objects.create(user=cls.user, name='task5', status='canceled')
        user2 = User.objects.create_user(username='foo', password='123456', email='')
        cls.other_task = Task.objects.create(user=user2, name='task6')

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        for view_name in ('pause_task', 'resume_task', 'cancel_task'):
            response = self.client.post(reverse(view_name, args=(self.ready_task.id,)))
            self.assertRedirects(response, reverse('login'))

    def test_not_found(self):
        """任务id不存在"""
        self.client.login(username='zzy', password='123456')
        for view_name in ('pause_task', 'resume_task', 'cancel_task'):
            response = self.client.post(reverse(view_name, args=(9999,)))
            self.assertEqual(404, response.status_code)

    def test_not_your_task(self):
        """任务id不属于当前用户"""
        self.client.login(username='zzy', password='123456')
        for view_name in ('pause_task', 'resume_task', 'cancel_task'):
            response = self.client.post(reverse(view_name, args=(self.other_task.id,)))
            self.assertEqual(403, response.status_code)
            self.assertEqual(b'Not your task', response.content)

    def test_operation_not_allowed(self):
        """操作不符合状态转移图"""
        self.client.login(username='zzy', password='123456')

        for task in (self.ready_task, self.running_task):
            response = self.client.get(reverse('resume_task', args=(task.id,)))
            self.assertEqual(403, response.status_code)
            self.assertEqual(b'Operation not allowed', response.content)

        response = self.client.get(reverse('pause_task', args=(self.paused_task.id,)))
        self.assertEqual(403, response.status_code)
        self.assertEqual(b'Operation not allowed', response.content)

        for task in (self.finished_task, self.canceled_task):
            for view_name in ('pause_task', 'resume_task', 'cancel_task'):
                response = self.client.get(reverse(view_name, args=(task.id,)))
                self.assertEqual(403, response.status_code)
                self.assertEqual(b'Operation not allowed', response.content)
