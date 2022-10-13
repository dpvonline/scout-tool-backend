# Generated by Django 4.1 on 2022-10-13 10:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageType',
            fields=[
                ('sorting', models.IntegerField(auto_created=True, null=True, unique=True)),
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=30)),
                ('is_comment', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('created_by_email', models.CharField(blank=True, max_length=60, null=True)),
                ('message_body', models.CharField(max_length=10000)),
                ('internal_comment', models.CharField(blank=True, max_length=10000, null=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('message_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messaging.messagetype')),
                ('supervisor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
