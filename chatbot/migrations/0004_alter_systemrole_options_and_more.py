# Generated by Django 5.1.4 on 2025-01-06 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0003_llmmodel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='systemrole',
            options={},
        ),
        migrations.RemoveField(
            model_name='systemrole',
            name='is_favorite',
        ),
        migrations.RemoveField(
            model_name='systemrole',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='systemrole',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='role_images/'),
        ),
    ]
