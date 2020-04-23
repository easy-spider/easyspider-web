from django.test import TestCase
from django.urls import reverse

from easyspider.models import User, Template, Task


class RegisterViewTests(TestCase):

    def test_register(self):
        """正常注册"""
        data = {'username': 'zzy', 'password': '1234'}
        response = self.client.post(reverse('easyspider:register'), data)
        self.assertRedirects(response, reverse('easyspider:index') + '?message=注册成功')

    def test_existing_username(self):
        """用户名已存在"""
        User.objects.create(username='zzy', password=User.encrypt_password('1234'))
        data = {'username': 'zzy', 'password': '1234'}
        response = self.client.post(reverse('easyspider:register'), data)
        self.assertContains(response, '用户名已存在')


class LoginViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='zzy', password=User.encrypt_password('1234'))

    def test_login(self):
        """正常登录"""
        data = {'username': 'zzy', 'password': '1234'}
        response = self.client.post(reverse('easyspider:login'), data, follow=True)
        self.assertRedirects(response, reverse('easyspider:index'))
        self.assertEqual(self.client.session.get('username'), 'zzy')
        self.assertContains(response, '欢迎，zzy！')

    def test_wrong_username(self):
        """用户名错误"""
        data = {'username': 'abc', 'password': '1234'}
        response = self.client.post(reverse('easyspider:login'), data)
        self.assertContains(response, '用户名或密码错误')

    def test_wrong_password(self):
        """密码错误"""
        data = {'username': 'zzy', 'password': '123'}
        response = self.client.post(reverse('easyspider:login'), data)
        self.assertContains(response, '用户名或密码错误')


class LogoutViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='zzy', password=User.encrypt_password('1234'))

    def test_logout(self):
        """正常注销"""
        data = {'username': 'zzy', 'password': '1234'}
        self.client.post(reverse('easyspider:login'), data, follow=True)
        response = self.client.get(reverse('easyspider:logout'), follow=True)
        self.assertRedirects(response, reverse('easyspider:index') + '?message=注销成功')
        self.assertNotIn('username', self.client.session)


class TemplateListViewTests(TestCase):

    def test_template_list(self):
        """爬虫模板列表"""
        Template.objects.create(name='A', path='/path/to/A')
        Template.objects.create(name='B', path='/path/to/B')
        response = self.client.get(reverse('easyspider:template-list'))
        self.assertQuerysetEqual(
            response.context['template_list'],
            ['<Template: A>', '<Template: B>'],
            ordered=False
        )

    def test_nothing(self):
        """列表为空"""
        response = self.client.get(reverse('easyspider:template-list'))
        self.assertQuerysetEqual(response.context['template_list'], [])


class TemplateDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.a = Template.objects.create(name='A', path='/path/to/A', params='foo;bar')
        Template.objects.create(name='B', path='/path/to/B')

    def test_template_detail(self):
        """模板详细信息"""
        response = self.client.get(reverse('easyspider:template-detail', args=(self.a.id,)))
        template = response.context['template']
        self.assertEqual(template.id, self.a.id)
        self.assertEqual(template.name, self.a.name)
        self.assertEqual(template.param_list(), ['foo', 'bar'])

    def test_not_found(self):
        """模板id不存在"""
        response = self.client.get(reverse('easyspider:template-detail', args=(9999,)))
        self.assertEqual(response.status_code, 404)


class CreateTaskViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.zzy = User.objects.create(username='zzy', password=User.encrypt_password('1234'))
        cls.template_a = Template.objects.create(name='A', path='/path/to/A', params='foo;bar')

    def test_create_task(self):
        """正常创建爬虫任务"""
        self.client.post(reverse('easyspider:login'), {'username': 'zzy', 'password': '1234'})
        data = {'template_id': self.template_a.id, 'name': 'task_a', 'foo': '123', 'bar': 'abc'}
        self.client.post(reverse('easyspider:create-task'), data)
        task = self.zzy.task_set.get()
        self.assertEqual(task.template_id, self.template_a.id)
        self.assertEqual(task.args_dict(), {'foo': '123', 'bar': 'abc'})


class ChangeTaskStatusViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.zzy = User.objects.create(username='zzy', password=User.encrypt_password('1234'))
        cls.template_a = Template.objects.create(name='A', path='/path/to/A', params='foo;bar')
        cls.task_a = Task.objects.create(
            user=cls.zzy, template=cls.template_a, name='task_a',
            args='{"foo": "123", "bar": "abc}', status='ready'
        )

    def test_start_task(self):
        """启动任务"""
        self.client.post(reverse('easyspider:login'), {'username': 'zzy', 'password': '1234'})
        self.client.get(reverse('easyspider:start-task', args=(self.task_a.id,)))
        task = Task.objects.get(pk=self.task_a.id)
        self.assertEqual(task.status, 'running')

    def test_not_found(self):
        """任务id不存在"""
        self.client.post(reverse('easyspider:login'), {'username': 'zzy', 'password': '1234'})
        response = self.client.get(reverse('easyspider:start-task', args=(9999,)))
        self.assertEqual(response.status_code, 404)

    def test_forbidden(self):
        """修改的任务不属于当前登录的用户"""
        User.objects.create(username='abc', password=User.encrypt_password('1234'))
        self.client.post(reverse('easyspider:login'), {'username': 'abc', 'password': '1234'})
        response = self.client.get(reverse('easyspider:start-task', args=(self.task_a.id,)))
        self.assertEqual(response.status_code, 403)
