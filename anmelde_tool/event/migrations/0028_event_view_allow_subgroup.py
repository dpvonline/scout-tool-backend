# Generated by Django 4.1.9 on 2023-10-14 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0025_remove_eventlocation_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='view_allow_subgroup',
            field=models.BooleanField(default=False),
        ),
    ]
