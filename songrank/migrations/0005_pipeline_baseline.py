# Generated by Django 3.1.4 on 2021-01-01 15:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songrank', '0004_auto_20210101_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipeline',
            name='baseline',
            field=models.DateField(default=datetime.date.today),
            preserve_default=False,
        ),
    ]
