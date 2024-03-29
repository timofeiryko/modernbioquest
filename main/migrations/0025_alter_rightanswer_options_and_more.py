# Generated by Django 4.1.3 on 2023-05-01 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_question_variant'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rightanswer',
            options={'ordering': ['parent_question', 'id'], 'verbose_name': 'Вариант или пункт', 'verbose_name_plural': 'Вариант или пункт'},
        ),
        migrations.RemoveField(
            model_name='solvedquestion',
            name='user_text',
        ),
        migrations.RemoveField(
            model_name='useranswer',
            name='is_right',
        ),
        migrations.AddField(
            model_name='useranswer',
            name='ratio',
            field=models.FloatField(null=True, verbose_name='Процент выполнения'),
        ),
        migrations.AddField(
            model_name='useranswer',
            name='user_flag_selected',
            field=models.BooleanField(blank=True, null=True, verbose_name='Вариант отмечен как верный'),
        ),
        migrations.AddField(
            model_name='useranswer',
            name='user_text',
            field=models.TextField(blank=True, null=True, verbose_name='Текстовый ответ пользователя'),
        ),
        migrations.AlterField(
            model_name='solvedquestion',
            name='user_score',
            field=models.FloatField(default=0.0, null=True, verbose_name='Балл пользователя'),
        ),
    ]
