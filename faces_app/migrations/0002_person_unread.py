# Generated by Django 4.1.3 on 2023-01-26 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faces_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='unread',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]