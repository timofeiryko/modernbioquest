# Generated by Django 4.1.3 on 2022-12-06 22:42

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_testquestion_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='slug',
            field=models.SlugField(default='vos', max_length=20, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')]),
        ),
    ]