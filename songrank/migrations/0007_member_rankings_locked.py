# Generated by Django 3.1.4 on 2021-04-13 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songrank', '0006_chop_chopper_rescue'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='rankings_locked',
            field=models.BooleanField(default=False),
        ),
    ]