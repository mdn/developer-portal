# Generated by Django 2.2.6 on 2019-10-01 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mozimages', '0001_initial'),
        ('events', '0018_update_event_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='social_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mozimages.MozImage'),
        ),
        migrations.AddField(
            model_name='events',
            name='social_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mozimages.MozImage'),
        ),
    ]
