# Generated by Django 4.1.5 on 2023-04-23 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("basic", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="eathabit",
            name="public",
            field=models.BooleanField(default=False),
        ),
    ]
