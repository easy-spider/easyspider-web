# Generated by Django 3.0.4 on 2020-05-01 05:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spiderTemplate', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='site',
            old_name='_type',
            new_name='site_type',
        ),
    ]