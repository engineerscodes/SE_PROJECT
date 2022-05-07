# Generated by Django 3.1.7 on 2021-06-25 04:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='videoUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('captions', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=100)),
                ('date', models.DateField(default='2001-04-12')),
                ('EventName', models.CharField(default='', max_length=50)),
                ('video', models.URLField(null=True, unique=True)),
                ('url_64encoding', models.CharField(default='/upload/videos/', max_length=2048)),
                ('Total_marks', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Marks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('videoId', models.CharField(max_length=250)),
                ('by_email', models.CharField(max_length=250)),
                ('marks', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('moderator_email', models.CharField(max_length=250)),
                ('video_link', models.CharField(max_length=100000)),
                ('date', models.DateField(default='2001-04-12')),
                ('EventName', models.CharField(default='', max_length=50)),
                ('verfiyed', models.BooleanField(default=False)),
            ],
            options={
                'unique_together': {('videoId', 'moderator_email')},
            },
        ),
    ]
