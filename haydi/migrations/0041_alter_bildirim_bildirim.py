# Generated by Django 4.1.7 on 2023-06-16 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haydi', '0040_rename_etkileşim_bildirim_etkilesim_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bildirim',
            name='bildirim',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]
