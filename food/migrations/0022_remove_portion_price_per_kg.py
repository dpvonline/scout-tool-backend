# Generated by Django 4.1.2 on 2023-01-15 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("food", "0021_remove_package_price_per_kg"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="portion",
            name="price_per_kg",
        ),
    ]
