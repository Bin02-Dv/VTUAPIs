# Generated by Django 5.0.3 on 2024-03-23 13:41

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VTUApp', '0002_apikey'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authapimodel',
            name='name',
        ),
        migrations.RemoveField(
            model_name='authapimodel',
            name='phone_number',
        ),
        migrations.AddField(
            model_name='authapimodel',
            name='username',
            field=models.CharField(default=1, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='authapimodel',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='authapimodel',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]
