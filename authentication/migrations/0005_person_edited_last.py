# Generated by Django 4.1.7 on 2023-02-26 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_alter_customuser_email_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='edited_last',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
