# Generated by Django 5.0 on 2023-12-19 11:54

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clonliner', '0003_alter_customer_joined_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='joined_on',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Введите дату регистрации пользователя', verbose_name='Дата регистрации пользователя'),
        ),
    ]
