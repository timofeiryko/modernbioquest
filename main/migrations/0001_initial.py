# Generated by Django 4.0.6 on 2022-07-25 17:04

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('text', models.TextField(null=True, verbose_name='Текст вопроса')),
                ('max_score', models.FloatField(default=1.0, null=True, verbose_name='Балл')),
                ('type', models.CharField(choices=[('P1', '1 правильный ответ'), ('P2', 'Множественный выбор'), ('REL', 'Соответствие'), ('STR', 'Текстовые пункты')], default='STR', max_length=4, verbose_name='Тип')),
                ('listed', models.BooleanField(blank=True, null=True, verbose_name='Публичный доступ')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.CharField(default='ВсОШ', max_length=300, null=True, verbose_name='Олимпиада')),
                ('link', models.CharField(max_length=300, validators=[django.core.validators.URLValidator()], verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Олимпиада',
                'verbose_name_plural': 'Олимпиады',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ImageAlbum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
            ],
            options={
                'verbose_name': 'Набор изображений',
                'verbose_name_plural': 'Наборы изображений',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.CharField(max_length=100, verbose_name='Название раздела')),
                ('slug', models.SlugField(max_length=100)),
            ],
            options={
                'verbose_name': 'Раздел',
                'verbose_name_plural': 'Разделы',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SolvedQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('user_text', models.TextField(null=True, verbose_name='Текст вопроса')),
                ('user_score', models.FloatField(default=0.0, null=True, verbose_name='Балл')),
                ('user_points', models.IntegerField(null=True, verbose_name='Количество верных ответов')),
                ('parent_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solved', to='main.basequestion')),
                ('solved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='solved_questions', to=settings.AUTH_USER_MODEL, verbose_name='Решено пользователем')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('label', models.TextField(null=True, verbose_name='Вариант или название пункта')),
                ('text', models.TextField(blank=True, null=True, verbose_name='Текстовый ответ')),
                ('flag', models.BooleanField(blank=True, null=True, verbose_name='Выбор варианта')),
                ('weight', models.FloatField(blank=True, null=True, verbose_name='Вес')),
                ('is_right', models.BooleanField(blank=True, null=True, verbose_name='Выбор варианта')),
                ('parent_solved', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='main.solvedquestion')),
            ],
            options={
                'verbose_name': 'Ответ пользователя',
                'verbose_name_plural': 'Ответы пользователей',
                'ordering': ['parent_solved'],
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.CharField(max_length=100, verbose_name='Тема')),
                ('parent_section', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='main.section', verbose_name='Раздел')),
            ],
            options={
                'verbose_name': 'Тема',
                'verbose_name_plural': 'Темы',
                'ordering': ['parent_section', 'name'],
            },
        ),
        migrations.CreateModel(
            name='RightAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('label', models.TextField(null=True, verbose_name='Вариант или название пункта')),
                ('text', models.TextField(blank=True, null=True, verbose_name='Текстовый ответ')),
                ('flag', models.BooleanField(blank=True, null=True, verbose_name='Выбор варианта')),
                ('weight', models.FloatField(blank=True, null=True, verbose_name='Вес')),
                ('parent_question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='right_answers', to='main.basequestion')),
            ],
            options={
                'verbose_name': 'Вариант или пункт',
                'verbose_name_plural': 'Вариант или пункт',
                'ordering': ['parent_question'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('file', models.ImageField(upload_to='images/', verbose_name='Файл')),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='main.imagealbum', verbose_name='Набор изображений')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
            },
        ),
        migrations.CreateModel(
            name='Explanation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('text', models.TextField(verbose_name='Разбор, комментарии')),
                ('mark', models.BooleanField(default=False, verbose_name='Проверено экспертом')),
                ('explauthor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Добавил разбор')),
                ('images', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.imagealbum', verbose_name='Иллюстрации к разбору')),
                ('parent_question', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.basequestion')),
            ],
            options={
                'verbose_name': 'Разбор',
                'verbose_name_plural': 'Разборы',
                'ordering': ['parent_question'],
            },
        ),
        migrations.AddField(
            model_name='basequestion',
            name='images',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.imagealbum', verbose_name='Иллюстрации к вопросу'),
        ),
        migrations.AddField(
            model_name='basequestion',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='basequestion',
            name='quauthor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to=settings.AUTH_USER_MODEL, verbose_name='Добавил вопрос'),
        ),
        migrations.AddField(
            model_name='basequestion',
            name='sections',
            field=models.ManyToManyField(blank=True, related_name='%(class)s', to='main.section', verbose_name='Разделы'),
        ),
        migrations.AddField(
            model_name='basequestion',
            name='topics',
            field=models.ManyToManyField(blank=True, related_name='%(class)s', to='main.topic', verbose_name='Темы'),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('basequestion_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.basequestion')),
                ('year', models.IntegerField(null=True, verbose_name='Год проведения')),
                ('stage', models.CharField(max_length=100, null=True, verbose_name='Этап')),
                ('grade', models.IntegerField(null=True, verbose_name='Класс')),
                ('part', models.CharField(max_length=100, null=True, verbose_name='Часть')),
                ('number', models.IntegerField(null=True, verbose_name='Номер')),
                ('competition', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='main.competition', verbose_name='Олимпиада')),
            ],
            options={
                'verbose_name': 'Вопрос с олимпиады',
                'verbose_name_plural': 'Вопросы с олимпиад',
                'ordering': ['-id'],
            },
            bases=('main.basequestion',),
        ),
    ]
