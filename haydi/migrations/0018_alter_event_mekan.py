# Generated by Django 4.2.1 on 2023-05-29 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('haydi', '0017_alter_event_açiklama'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='mekan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='etkinlikler', to='haydi.mekan'),
        ),
    ]
