# Generated by Django 3.0.4 on 2020-05-03 09:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('scheduler', '0001_initial'),
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='task.Task'),
        ),
    ]
