# Generated by Django 4.2.1 on 2023-05-25 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haydi', '0011_profile_activity_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='katildigi_etkinlikler',
            field=models.ManyToManyField(blank=True, related_name='katilimcilar_profil', to='haydi.event'),
        ),
    ]