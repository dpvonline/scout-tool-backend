# Generated by Django 4.1.2 on 2022-10-23 14:57

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KeycloakRole',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('keycloak_id', models.CharField(max_length=36)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='KeycloakGroup',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('keycloak_id', models.CharField(max_length=36)),
                ('name', models.CharField(max_length=100)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='keycloak_group', to='keycloak_auth.keycloakgroup')),
                ('roles', models.ManyToManyField(blank=True, to='keycloak_auth.keycloakrole')),
            ],
        ),
    ]
