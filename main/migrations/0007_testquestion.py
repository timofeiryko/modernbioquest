# Generated by Django 4.0.6 on 2022-08-13 21:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_rightanswer_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestQuestion',
            fields=[
                ('basequestion_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.basequestion')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.basequestion',),
        ),
    ]
