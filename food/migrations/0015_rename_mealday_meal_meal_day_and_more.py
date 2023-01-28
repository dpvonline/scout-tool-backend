# Generated by Django 4.1.2 on 2022-12-02 17:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("food", "0014_event_meal_mealitem_mealday_meal_mealday"),
    ]

    operations = [
        migrations.RenameField(
            model_name="meal",
            old_name="mealDay",
            new_name="meal_day",
        ),
        migrations.RenameField(
            model_name="meal",
            old_name="mealType",
            new_name="meal_type",
        ),
        migrations.AlterField(
            model_name="mealday",
            name="date",
            field=models.DateField(default=datetime.datetime),
        ),
    ]
