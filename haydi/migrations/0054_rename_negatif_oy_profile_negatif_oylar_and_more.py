# Generated by Django 4.1.7 on 2023-07-11 10:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('haydi', '0053_profile_negatif_oy_profile_pozitif_oy'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='negatif_oy',
            new_name='negatif_oylar',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='pozitif_oy',
            new_name='pozitif_oylar',
        ),
    ]
