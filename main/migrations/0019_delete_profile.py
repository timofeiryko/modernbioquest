# Generated by Django 4.1.3 on 2023-02-21 18:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0018_remove_question_stage"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Profile",
        ),
    ]
