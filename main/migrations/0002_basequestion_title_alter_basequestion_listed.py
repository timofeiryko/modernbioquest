# Generated by Django 4.0.6 on 2022-07-25 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basequestion',
            name='title',
            field=models.CharField(max_length=100, null=True, verbose_name='Текст вопроса'),
        ),
        migrations.AlterField(
            model_name='basequestion',
            name='listed',
            field=models.BooleanField(null=True, verbose_name='Публичный доступ'),
        ),
    ]
