# Generated by Django 5.1.6 on 2025-02-27 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhook_app', '0002_webhooklog_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhooklog',
            name='source',
            field=models.CharField(default='unknown', max_length=50),
        ),
    ]
