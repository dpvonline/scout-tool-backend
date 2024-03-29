# Generated by Django 4.1.5 on 2023-02-05 18:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("messaging", "0002_message_message_subject"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="created_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="created_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="message_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="messaging.messagetype"
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="supervisor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="supervisor",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
