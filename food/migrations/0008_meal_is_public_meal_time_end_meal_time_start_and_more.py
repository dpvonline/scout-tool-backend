# Generated by Django 4.1.9 on 2023-10-02 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0007_alter_recipe_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='meal',
            name='time_end',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='meal',
            name='time_start',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mealday',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
