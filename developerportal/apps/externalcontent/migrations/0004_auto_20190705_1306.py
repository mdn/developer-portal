# Generated by Django 2.2.3 on 2019-07-05 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0003_externalarticle_externalevent_externalvideo'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalarticle',
            name='readtime',
            field=models.CharField(blank=True, default='0 min read', max_length=30),
        ),
        migrations.AddField(
            model_name='externalvideo',
            name='video_duration',
            field=models.CharField(blank=True, default='0:00', max_length=30),
        ),
    ]
