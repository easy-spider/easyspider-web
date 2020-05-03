# Generated by Django 3.0.4 on 2020-05-03 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('spiderTemplate', '0003_auto_20200501_2351'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('finish_time', models.DateTimeField(blank=True, null=True)),
                ('args', models.CharField(max_length=4095, null=True)),
                ('status', models.CharField(choices=[('ready', '等待运行'), ('running', '正在运行'), ('paused', '暂停运行'), ('finished', '完成运行'), ('canceled', '已终止')], default='ready', max_length=10)),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='spiderTemplate.Template')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
