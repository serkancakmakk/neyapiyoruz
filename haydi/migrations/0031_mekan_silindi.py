# Generated by Django 4.2.1 on 2023-06-08 11:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("haydi", "0030_yorumcevap_yorum_alter_yorumcevap_cevap"),
    ]

    operations = [
        migrations.AddField(
            model_name="mekan",
            name="silindi",
            field=models.BooleanField(default="False", verbose_name="Silindi"),
        ),
    ]