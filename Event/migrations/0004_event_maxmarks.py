# Generated by Django 3.1.7 on 2021-08-03 18:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Event', '0003_auto_20210625_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='maxMarks',
            field=models.IntegerField(default=100, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(1)]),
        ),
    ]