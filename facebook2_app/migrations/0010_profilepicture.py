# Generated by Django 4.1.3 on 2023-01-19 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facebook2_app', '0009_alter_comment_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilePicture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('person', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='facebook2_app.person')),
            ],
        ),
    ]