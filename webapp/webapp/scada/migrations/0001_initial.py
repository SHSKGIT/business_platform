# Generated by Django 5.1 on 2024-08-15 20:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('comment', models.TextField()),
                ('date', models.DateTimeField(default=datetime.datetime(2024, 8, 15, 14, 49, 5, 514162))),
            ],
        ),
    ]
