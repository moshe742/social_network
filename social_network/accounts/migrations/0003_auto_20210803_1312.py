# Generated by Django 3.2 on 2021-08-03 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_ip'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='time_zone',
        ),
        migrations.DeleteModel(
            name='TimeZone',
        ),
    ]
