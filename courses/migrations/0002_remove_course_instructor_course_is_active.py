# Generated by Django 5.1.3 on 2024-11-19 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='instructor',
        ),
        migrations.AddField(
            model_name='course',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
