import os

from django.test import TestCase
from django.urls import reverse

from pic import views


class SiteLogoViewTests(TestCase):

    def test_ok(self):
        response = self.client.get(reverse('pic:site-logo', args=('test',)))
        self.assertEqual(200, response.status_code)
        with open(os.path.join(views.PIC_DIR, 'test/logo.jpg'), 'rb') as f:
            self.assertEqual(f.read(), response.content)

    def test_not_found(self):
        response = self.client.get(reverse('pic:site-logo', args=('abc',)))
        self.assertEqual(404, response.status_code)

    def test_forbidden(self):
        response = self.client.get(reverse('pic:site-logo', args=('..',)))
        self.assertEqual(403, response.status_code)


class TemplateLogoViewTests(TestCase):

    def test_ok(self):
        response = self.client.get(reverse('pic:template-logo', args=('test', 'movie')))
        self.assertEqual(200, response.status_code)
        with open(os.path.join(views.PIC_DIR, 'test/movie/logo.jpg'), 'rb') as f:
            self.assertEqual(f.read(), response.content)

    def test_not_found(self):
        response = self.client.get(reverse('pic:template-logo', args=('test', 'book')))
        self.assertEqual(404, response.status_code)

    def test_forbidden(self):
        response = self.client.get(reverse('pic:template-logo', args=('..', '..')))
        self.assertEqual(403, response.status_code)


class TemplateFieldViewTests(TestCase):

    def test_ok(self):
        response = self.client.get(reverse('pic:template-field', args=('test', 'movie', 'title')))
        self.assertEqual(200, response.status_code)
        with open(os.path.join(views.PIC_DIR, 'test/movie/field/title.jpg'), 'rb') as f:
            self.assertEqual(f.read(), response.content)

    def test_not_found(self):
        response = self.client.get(reverse('pic:template-field', args=('test', 'movie', 'name')))
        self.assertEqual(404, response.status_code)

    def test_forbidden(self):
        response = self.client.get(reverse('pic:template-field', args=('..', '..', '..')))
        self.assertEqual(403, response.status_code)


class TemplateParamViewTests(TestCase):

    def test_ok(self):
        response = self.client.get(reverse('pic:template-param', args=('test', 'movie', 'page')))
        self.assertEqual(200, response.status_code)
        with open(os.path.join(views.PIC_DIR, 'test/movie/param/page.jpg'), 'rb') as f:
            self.assertEqual(f.read(), response.content)

    def test_not_found(self):
        response = self.client.get(reverse('pic:template-param', args=('test', 'movie', 'date')))
        self.assertEqual(404, response.status_code)

    def test_forbidden(self):
        response = self.client.get(reverse('pic:template-param', args=('..', '..', '..')))
        self.assertEqual(403, response.status_code)
