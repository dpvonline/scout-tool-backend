# Generated by Django 4.1.13 on 2024-01-07 17:33

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0004_deploy_scout_hierachies'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frontendtheme',
            name='accent',
            field=colorfield.fields.ColorField(default='#82B1FF', image_field=None, max_length=25, samples=None),
        ),
        migrations.AlterField(
            model_name='frontendtheme',
            name='error',
            field=colorfield.fields.ColorField(default='#FF5252', image_field=None, max_length=25, samples=None),
        ),
        migrations.AlterField(
            model_name='frontendtheme',
            name='info',
            field=colorfield.fields.ColorField(default='#2196F3', image_field=None, max_length=25, samples=None),
        ),
        migrations.AlterField(
            model_name='frontendtheme',
            name='primary',
            field=colorfield.fields.ColorField(default='#1976D2', image_field=None, max_length=25, samples=None),
        ),
        migrations.AlterField(
            model_name='frontendtheme',
            name='secondary',
            field=colorfield.fields.ColorField(default='#424242', image_field=None, max_length=25, samples=None),
        ),
        migrations.AlterField(
            model_name='frontendtheme',
            name='success',
            field=colorfield.fields.ColorField(default='#4CAF50', image_field=None, max_length=25, samples=None),
        ),
        migrations.AlterField(
            model_name='frontendtheme',
            name='warning',
            field=colorfield.fields.ColorField(default='#FFC107', image_field=None, max_length=25, samples=None),
        ),
        migrations.AlterField(
            model_name='tagtype',
            name='color',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None),
        ),
    ]
