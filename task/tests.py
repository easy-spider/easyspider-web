import json
from uuid import uuid4

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from scheduler.models import Job
from scheduler.views import JobStatus
from spiderTemplate.models import Site, Template, Param
from task.models import Task


def create_test_data():
    site = Site.objects.create(name='S1', display_name='S1', egg='')
    template = Template.objects.create(
        site=site, name='T1', display_name='T1',
        introduction='', split_param='p2', sample_data=''
    )
    Param.objects.create(
        template=template, name='p1', display_name='p1',
        input_type='text', length_limit=10
    )
    Param.objects.create(
        template=template, name='p2', display_name='p2',
        input_type='number', number_min=100, number_max=999
    )
    return template


class TaskModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='zzy', password='123456', email='')
        cls.template = create_test_data()

    def test_set_name_invalid_length(self):
        """任务名称长度不在规定的范围内"""
        task = Task(user=self.user, template=self.template)
        for name in ('t1', ' t1 ', '     ', 't' * 30):
            with self.assertRaises(ValueError) as cm:
                task.set_name(name)
            self.assertEqual('任务名长度应在3~20个字符之间', cm.exception.args[0])

    def test_name_already_exists(self):
        """任务名称已存在"""
        Task.objects.create(user=self.user, template=self.template, name='task1')
        task = Task(user=self.user, template=self.template)
        with self.assertRaises(ValueError) as cm:
            task.set_name(' task1\t\r\n')
        self.assertEqual('任务名称已存在', cm.exception.args[0])
        # 重新运行任务时如果未修改任务名称则不应报错（名称与自己重复）
        task = self.user.task_set.get()
        task.set_name(' task1 ')
        self.assertEqual('task1', task.name)

    def test_set_name(self):
        task = Task(user=self.user, template=self.template)
        task.set_name('  task1\t\r\n')
        self.assertEqual('task1', task.name)

    def test_invalid_arg(self):
        task = Task.objects.create(user=self.user, template=self.template, name='task1')
        with self.assertRaises(ValueError) as cm:
            task.set_args({'p1': 'a' * 20, 'p2': '123'})
        self.assertEqual('p1的长度不能超过10', cm.exception.args[0])
        for p2 in (8, 99, 1000, 2000):
            with self.assertRaises(ValueError) as cm:
                task.set_args({'p1': 'abc', 'p2': p2})
            self.assertEqual('p2的值应在100~999之间', cm.exception.args[0])

    def test_set_args(self):
        task = Task.objects.create(user=self.user, template=self.template, name='task1')
        split_arg = task.set_args({'p1': 'abc', 'p2': '123', 'p3': 'what'})
        self.assertEqual('{"p1": "abc", "p2": 123}', task.args)
        self.assertEqual({'p1': 'abc', 'p2': 123}, task.args_dict())
        self.assertEqual(123, split_arg)

    def test_display_status(self):
        task = Task.objects.create(user=self.user, template=self.template, name='task1')
        for s in Task.STATUS_CHOICES:
            task.status = s[0]
            self.assertEqual(s[1], task.display_status())


class CreateTaskViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='zzy', password='123456', email='')
        cls.template = create_test_data()

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
            self.assertEqual({'status': 'ERROR', 'message': '任务名长度应在3~20个字符之间'}, response.json())

    def test_name_already_exists(self):
        """任务名称已存在"""
        self.client.login(username='zzy', password='123456')
        Task.objects.create(user=self.user, template=self.template, name='task1')
        data = {'inputTaskName': ' task1\t\r\n', 'p1': 'abc', 'p2': '42'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual({'status': 'ERROR', 'message': '任务名称已存在'}, response.json())

    def test_invalid_arg(self):
        self.client.login(username='zzy', password='123456')
        data = {'inputTaskName': 'task1', 'p1': 'a' * 20, 'p2': '123'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual(
            {'status': 'ERROR', 'message': 'p1的长度不能超过10'},
            response.json()
        )

        data['p1'] = 'abc'
        for p2 in (8, 99, 1000, 2000):
            data['p2'] = p2
            response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
            self.assertEqual(
                {'status': 'ERROR', 'message': 'p2的值应在100~999之间'},
                response.json()
            )

    def test_ok(self):
        """成功创建task和job"""
        self.client.login(username='zzy', password='123456')
        data = {'inputTaskName': 'task1', 'p1': 'abc', 'p2': '123'}
        response = self.client.post(reverse('create_task', args=(self.template.id,)), data)
        self.assertEqual('SUCCESS', response.json()['status'])

        task = Task.objects.filter(user=self.user, template=self.template).first()
        self.assertEqual('task1', task.name)
        jobs = task.job_set.all()
        self.assertEqual({'abc'}, {json.loads(j.args)['p1'] for j in jobs})
        self.assertEqual(set(range(1, 124)), {json.loads(j.args)['p2'] for j in jobs})


class TaskListViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        t = create_test_data()
        for username in ('foo', 'bar'):
            user = User.objects.create_user(username=username, password='123456', email='')
            for i in range(1, 3):
                Task.objects.create(user=user, template=t, name='{}_task{}'.format(username, i))

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
        template = create_test_data()
        cls.foo = User.objects.create_user(username='foo', password='123456', email='')
        cls.foo_task = Task.objects.create(user=cls.foo, template=template, name='foo_task1')
        Task.objects.create(user=cls.foo, template=template, name='foo_task2')
        cls.bar = User.objects.create_user(username='bar', password='123456', email='')
        cls.bar_task = Task.objects.create(user=cls.bar, template=template, name='bar_task1')

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
            self.assertEqual({'status': 'ERROR', 'message': '任务名长度应在3~20个字符之间'}, response.json())

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
        template = create_test_data()
        # 每种状态的任务关联的作业可能存在的状态
        status_map = {
            'ready': [JobStatus.CREATED, JobStatus.PENDING],
            'running': [JobStatus.CREATED, JobStatus.PENDING, JobStatus.RUNNING,
                        JobStatus.FINISHED],
            'paused': [JobStatus.CREATED, JobStatus.RUNNING, JobStatus.FINISHED],
            'finished': [JobStatus.FINISHED],
            'canceled': [JobStatus.FINISHED]
        }
        for i, task_status in enumerate(status_map):
            task = Task.objects.create(
                user=cls.user, template=template,
                name='task{}'.format(i + 1), status=task_status
            )
            for job_status in status_map[task_status]:
                Job.objects.create(uuid=uuid4(), task=task, status=job_status)
        cls.user2 = User.objects.create_user(username='foo', password='123456', email='')
        Task.objects.create(user=cls.user2, template=template, name='task6')

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        any_task = Task.objects.all()[0]
        for view_name in ('pause_task', 'resume_task', 'cancel_task'):
            response = self.client.post(reverse(view_name, args=(any_task.id,)))
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
        other_task = self.user2.task_set.get()
        for view_name in ('pause_task', 'resume_task', 'cancel_task'):
            response = self.client.post(reverse(view_name, args=(other_task.id,)))
            self.assertEqual(403, response.status_code)
            self.assertEqual(b'Not your task', response.content)

    def test_operation_not_allowed(self):
        """操作不符合状态转移图"""
        self.client.login(username='zzy', password='123456')

        # {view_name: [allowed_status]}
        status_map = {
            'pause_task': ['ready', 'paused', 'finished', 'canceled'],
            'resume_task': ['ready', 'running', 'finished', 'canceled'],
            'cancel_task': ['finished', 'canceled']
        }
        for view_name in status_map:
            for s in status_map[view_name]:
                task = self.user.task_set.get(status=s)
                response = self.client.post(reverse(view_name, args=(task.id,)))
                self.assertEqual(403, response.status_code)
                self.assertEqual(b'Operation not allowed', response.content)

    def test_pause(self):
        """running状态的任务可暂停，所有PENDING状态的作业改为CREATED"""
        self.client.login(username='zzy', password='123456')
        task = self.user.task_set.get(status='running')
        response = self.client.post(reverse('pause_task', args=(task.id,)))
        self.assertEqual({'status': 'SUCCESS'}, response.json())
        task = Task.objects.get(pk=task.id)
        self.assertEqual('paused', task.status)
        self.assertFalse(task.job_set.filter(status=JobStatus.PENDING).exists())

    def test_resume(self):
        """paused状态的任务可继续，作业状态没有改变"""
        self.client.login(username='zzy', password='123456')
        task = self.user.task_set.get(status='paused')
        response = self.client.post(reverse('resume_task', args=(task.id,)))
        self.assertEqual({'status': 'SUCCESS'}, response.json())
        task = Task.objects.get(pk=task.id)
        self.assertEqual('running', task.status)

    def test_cancel(self):
        """ready, running和paused状态的任务可终止，所有作业状态改为FINISHED"""
        self.client.login(username='zzy', password='123456')
        for s in ('ready', 'running', 'paused'):
            task = self.user.task_set.get(status=s)
            response = self.client.post(reverse('cancel_task', args=(task.id,)))
            self.assertEqual({'status': 'SUCCESS'}, response.json())
            task = Task.objects.get(pk=task.id)
            self.assertEqual('canceled', task.status)
            self.assertFalse(task.job_set.exclude(status=JobStatus.FINISHED).exists())


class DeleteTaskViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='zzy', password='123456', email='')
        template = create_test_data()
        for i, s in enumerate(Task.STATUS_CHOICES):
            task = Task.objects.create(
                user=cls.user, template=template,
                name='task{}'.format(i + 1), status=s[0]
            )
            Job.objects.create(uuid=uuid4(), task=task)
        cls.user2 = User.objects.create_user(username='foo', password='123456', email='')
        Task.objects.create(user=cls.user2, template=template, name='task6')

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        any_task = Task.objects.all()[0]
        response = self.client.post(reverse('delete_task', args=(any_task.id,)))
        self.assertRedirects(response, reverse('login'))

    def test_not_found(self):
        """任务id不存在"""
        self.client.login(username='zzy', password='123456')
        response = self.client.post(reverse('delete_task', args=(9999,)))
        self.assertEqual(404, response.status_code)

    def test_not_your_task(self):
        """任务id不属于当前用户"""
        self.client.login(username='zzy', password='123456')
        other_task = self.user2.task_set.get()
        response = self.client.post(reverse('delete_task', args=(other_task.id,)))
        self.assertEqual(403, response.status_code)
        self.assertEqual(b'Not your task', response.content)

    def test_operation_not_allowed(self):
        """不是finished和canceled状态的任务不能删除"""
        self.client.login(username='zzy', password='123456')

        for s in ('ready', 'running', 'paused'):
            task = self.user.task_set.get(status=s)
            response = self.client.post(reverse('delete_task', args=(task.id,)))
            self.assertEqual(403, response.status_code)
            self.assertEqual(b'Operation not allowed', response.content)

    def test_ok(self):
        self.client.login(username='zzy', password='123456')
        for s in ('finished', 'canceled'):
            task = self.user.task_set.get(status=s)
            response = self.client.post(reverse('delete_task', args=(task.id,)))
            self.assertEqual({'status': 'SUCCESS'}, response.json())
            self.assertFalse(Task.objects.filter(pk=task.id).exists())
            self.assertFalse(Job.objects.filter(task_id=task.id).exists())


class ClearDataViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='zzy', password='123456', email='')
        template = create_test_data()
        for i, s in enumerate(Task.STATUS_CHOICES):
            Task.objects.create(
                user=cls.user, template=template,
                name='task{}'.format(i + 1), status=s[0]
            )
        cls.user2 = User.objects.create_user(username='foo', password='123456', email='')
        Task.objects.create(user=cls.user2, template=template, name='task6')

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        any_task = Task.objects.all()[0]
        response = self.client.post(reverse('clear_data', args=(any_task.id,)))
        self.assertRedirects(response, reverse('login'))

    def test_not_found(self):
        """任务id不存在"""
        self.client.login(username='zzy', password='123456')
        response = self.client.post(reverse('clear_data', args=(9999,)))
        self.assertEqual(404, response.status_code)

    def test_not_your_task(self):
        """任务id不属于当前用户"""
        self.client.login(username='zzy', password='123456')
        other_task = self.user2.task_set.get()
        response = self.client.post(reverse('clear_data', args=(other_task.id,)))
        self.assertEqual(403, response.status_code)
        self.assertEqual(b'Not your task', response.content)

    def test_operation_not_allowed(self):
        """不是finished和canceled状态的任务不能清除数据"""
        self.client.login(username='zzy', password='123456')

        for s in ('ready', 'running', 'paused'):
            task = self.user.task_set.get(status=s)
            response = self.client.post(reverse('clear_data', args=(task.id,)))
            self.assertEqual(403, response.status_code)
            self.assertEqual(b'Operation not allowed', response.content)
