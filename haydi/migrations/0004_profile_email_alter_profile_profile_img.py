# Generated by Django 4.1.7 on 2023-05-24 14:49

from django.db import migrations, models
import haydi.models


class Migration(migrations.Migration):

    dependencies = [
        ('haydi', '0003_profile_remove_event_katilimcilar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_img',
            field=models.ImageField(default='default.jpg', upload_to=haydi.models.user_directory_path),
        ),
    ]
