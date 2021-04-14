# Generated by Django 3.1.4 on 2021-04-14 14:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('songrank', '0008_songchop'),
    ]

    operations = [
        migrations.CreateModel(
            name='SongComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True)),
                ('date', models.DateField()),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='song_comments', to=settings.AUTH_USER_MODEL)),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='songrank.song')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='ChopperComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True)),
                ('date', models.DateField()),
                ('chopper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='songrank.chopper')),
                ('commenter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chopper_comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
    ]
