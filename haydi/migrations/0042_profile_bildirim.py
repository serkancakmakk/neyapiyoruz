# Generated by Django 4.1.7 on 2023-06-16 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('haydi', '0041_alter_bildirim_bildirim'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bildirim',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='haydi.bildirim'),
        ),
    ]
