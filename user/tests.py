from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegisterViewTests(TestCase):

    def test_get(self):
        response = self.client.get(reverse('register'))
        self.assertTemplateUsed(response, 'user/register.html')

    def test_post(self):
        """正常注册"""
        data = {
            'username': 'zzy', 'password': '123456',
            'email': 'zzy@example.com', 'first_name': 'ZZy'
        }
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('index'))
        user = authenticate(username='zzy', password='123456')
        self.assertIsNotNone(user)
        self.assertEqual('zzy@example.com', user.email)
        self.assertEqual('ZZy', user.first_name)

    def test_existing_username(self):
        """用户名已存在"""
        User.objects.create_user(username='zzy', password='123456', email='zzy@example.com')
        data = {
            'username': 'zzy', 'password': 'abcdef',
            'email': 'zzy@foobar.com', 'first_name': 'ZZy'
        }
        response = self.client.post(reverse('register'), data)
        self.assertContains(response, '用户名已存在')


class LoginViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='zzy', password='123456', email='zzy@example.com')

    def test_login(self):
        """正常登录"""
        data = {'username': 'zzy', 'password': '123456', 'email': 'zzy@foobar.com'}
        response = self.client.post(reverse('login'), data, follow=True)
        self.assertRedirects(response, reverse('starter'))
        self.assertTrue(hasattr(response.wsgi_request, 'user'))
        self.assertEqual('zzy', response.wsgi_request.user.username)

    def test_wrong_username(self):
        """用户名错误"""
        data = {'username': 'abc', 'password': '123456'}
        response = self.client.post(reverse('login'), data)
        self.assertContains(response, '用户名或密码错误')

    def test_wrong_password(self):
        """密码错误"""
        data = {'username': 'zzy', 'password': '1234'}
        response = self.client.post(reverse('login'), data)
        self.assertContains(response, '用户名或密码错误')


class LogoutViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='zzy', password='123456', email='zzy@example.com')

    def test_logout(self):
        """正常注销"""
        data = {'username': 'zzy', 'password': '123456'}
        self.client.post(reverse('login'), data, follow=True)
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, reverse('index'))
        self.assertNotEqual('zzy', response.wsgi_request.user.username)


class UserProfileViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(
            username='zzy', password='123456',
            email='zzy@example.com', first_name='ZZy'
        )

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        response = self.client.get(reverse('user_profile'))
        self.assertRedirects(response, reverse('login'))
        data = {'email': 'zzy2@example.com', 'first_name': 'ZZy979'}
        response = self.client.post(reverse('user_profile'), data)
        self.assertRedirects(response, reverse('login'))

    def test_get(self):
        self.client.login(username='zzy', password='123456')
        response = self.client.get(reverse('user_profile'))
        self.assertTemplateUsed(response, 'user/information.html')

    def test_post(self):
        self.client.login(username='zzy', password='123456')
        data = {'email': 'zzy2@example.com', 'first_name': 'ZZy979'}
        response = self.client.post(reverse('user_profile'), data, follow=True)
        self.assertEqual(
            [(reverse('index'), 302), (reverse('starter'), 302)],
            response.redirect_chain
        )
        user = User.objects.get(username='zzy')
        self.assertEqual('zzy2@example.com', user.email)
        self.assertEqual('ZZy979', user.first_name)


class ResetPasswordViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='zzy', password='123456')

    def test_get(self):
        response = self.client.get(reverse('reset_password'))
        self.assertTemplateUsed(response, 'user/reset_password.html')

    def test_not_login(self):
        """未登录时重定向到登录页面"""
        response = self.client.post(reverse('reset_password'), {'password': '654321'})
        self.assertRedirects(response, reverse('login'))

    def test_post(self):
        """正常修改密码"""
        self.client.login(username='zzy', password='123456')
        response = self.client.post(reverse('reset_password'), {'password': '654321'}, follow=True)
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        user = authenticate(username='zzy', password='654321')
        self.assertIsNotNone(user)
