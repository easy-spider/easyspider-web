# Generated by Django 3.0.4 on 2020-04-23 06:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=50)),
                ('port', models.IntegerField()),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('status', models.IntegerField(default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('introduction', models.CharField(max_length=2047, null=True)),
                ('path', models.CharField(max_length=2047)),
                ('params', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, unique=True)),
                ('password', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('args', models.CharField(max_length=4095, null=True)),
                ('status', models.CharField(choices=[('ready', '等待运行'), ('running', '正在运行'), ('paused', '暂停运行'), ('finished', '完成运行')], max_length=10)),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='easyspider.Template')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='easyspider.User')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('ready', '等待运行'), ('running', '正在运行'), ('paused', '暂停运行'), ('finished', '完成运行')], max_length=10)),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='easyspider.Node')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='easyspider.Task')),
            ],
        ),
    ]
