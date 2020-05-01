from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegisterViewTests(TestCase):

    def test_register(self):
        """正常注册"""
        data = {'username': 'zzy', 'password': '123456', 'email': 'zzy@example.com'}
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('index'))
        user = authenticate(username='zzy', password='123456')
        self.assertIsNotNone(user)

    def test_existing_username(self):
        """用户名已存在"""
        User.objects.create_user(username='zzy', password='123456', email='zzy@example.com')
        data = {'username': 'zzy', 'password': 'abcdef', 'email': 'zzy@foobar.com'}
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
        self.assertEqual(response.wsgi_request.user.username, 'zzy')

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
        self.assertNotEqual(response.wsgi_request.user.username, 'zzy')
