# Generated by Django 4.0.6 on 2022-07-25 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_basequestion_title_alter_basequestion_listed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basequestion',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Заголовок'),
        ),
    ]
