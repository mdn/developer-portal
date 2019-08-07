# Generated by Django 2.2.4 on 2019-08-07 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0002_video_related_links_mdn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='description',
            field=models.TextField(blank=True, default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='video',
            name='duration',
            field=models.CharField(blank=True, help_text='Optional. Video duration in MM:SS format e.g. “12:34”. Shown as a small hint when the video is displayed as a card.', max_length=30, null=True),
        ),
    ]
