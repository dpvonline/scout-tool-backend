# Generated by Django 4.1.8 on 2023-05-04 19:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cash', '0003_alter_cashincome_registration'),
        ('attributes', '0006_alter_booleanattribute_registration_and_more'),
        ('event', '0021_remove_registration_event_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Registration',
        ),
        migrations.DeleteModel(
            name='RegistrationParticipant',
        ),
        migrations.DeleteModel(
            name='Workshop',
        ),
        migrations.DeleteModel(
            name='WorkshopParticipant',
        ),
    ]
