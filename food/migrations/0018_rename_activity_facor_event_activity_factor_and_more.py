# Generated by Django 4.1.2 on 2022-12-18 00:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("food", "0017_physicalactivitylevel_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="event",
            old_name="activity_facor",
            new_name="activity_factor",
        ),
        migrations.AlterField(
            model_name="meal",
            name="meal_day",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="food.mealday",
            ),
        ),
        migrations.AlterField(
            model_name="meal",
            name="meal_type",
            field=models.CharField(
                choices=[
                    ("breakfast", "Frühstück"),
                    ("lunch_warm", "Menu (warm)"),
                    ("lunch_cold", "Menu (kalt)"),
                    ("snack", "Snack"),
                ],
                default="lunch_warm",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="meal",
            name="name",
            field=models.CharField(
                blank=True, default="Hauptessen", max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="mealday",
            name="activity_facor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="food.physicalactivitylevel",
            ),
        ),
        migrations.AlterField(
            model_name="mealday",
            name="date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="meal_type",
            field=models.CharField(
                choices=[
                    ("breakfast", "Frühstück"),
                    ("lunch_warm", "Menu (warm)"),
                    ("lunch_cold", "Menu (kalt)"),
                    ("snack", "Snack"),
                ],
                default="lunch_warm",
                max_length=11,
            ),
        ),
    ]
