# Generated by Django 4.2.1 on 2023-06-10 09:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("haydi", "0036_mekan_olumlu_oy_kullananlar_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mekan",
            name="olumlu_oy_kullananlar",
            field=models.ManyToManyField(
                blank=True,
                null=True,
                related_name="olumlu_oylar",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="mekan",
            name="olumsuz_oy_kullananlar",
            field=models.ManyToManyField(
                blank=True,
                null=True,
                related_name="olumsuz_oylar",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
