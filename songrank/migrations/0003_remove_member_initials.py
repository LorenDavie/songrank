# Generated by Django 3.1.4 on 2020-12-24 18:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('songrank', '0002_auto_20201224_1501'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='initials',
        ),
    ]
