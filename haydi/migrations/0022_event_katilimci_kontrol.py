# Generated by Django 4.2.1 on 2023-06-03 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haydi', '0021_event_katilimci_sayisi'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='katilimci_kontrol',
            field=models.BooleanField(default=False),
        ),
    ]