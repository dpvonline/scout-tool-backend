# Generated by Django 4.1.3 on 2022-11-08 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0011_alter_requestgroupaccess_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='keycloak_id',
            field=models.CharField(blank=True, editable=False, max_length=32, null=True, unique=True),
        ),
    ]
