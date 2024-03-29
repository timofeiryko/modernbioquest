# Generated by Django 4.1.3 on 2022-12-08 21:53

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_question_number_others'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='slug',
            field=models.SlugField(default='vos', validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')]),
        ),
        migrations.AlterField(
            model_name='section',
            name='slug',
            field=models.SlugField(max_length=100, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')]),
        ),
    ]
