# Generated by Django 4.1.7 on 2023-06-17 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haydi', '0044_alter_bildirim_bildirim_alani_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bildirim_sayisi',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
