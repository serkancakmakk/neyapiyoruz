# Generated by Django 4.2.1 on 2023-06-09 08:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("haydi", "0034_remove_mekan_kapali_mekan_acik"),
    ]

    operations = [
        migrations.AddField(
            model_name="mekan",
            name="olumlu_oy",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="mekan",
            name="olumsuz_oy",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
