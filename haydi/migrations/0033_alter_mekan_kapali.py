# Generated by Django 4.2.1 on 2023-06-08 15:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("haydi", "0032_mekan_kapali"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mekan",
            name="kapali",
            field=models.BooleanField(default=False, verbose_name="Kapalı"),
        ),
    ]