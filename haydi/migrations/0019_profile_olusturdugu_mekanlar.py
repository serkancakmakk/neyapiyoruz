# Generated by Django 4.2.1 on 2023-05-31 08:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('haydi', '0018_alter_event_mekan'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='olusturdugu_mekanlar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='haydi.mekan'),
        ),
    ]
