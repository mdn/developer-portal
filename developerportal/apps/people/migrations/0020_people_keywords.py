# Generated by Django 2.2.3 on 2019-07-25 12:26

from django.db import migrations
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('people', '0019_remove_people_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='people',
            name='keywords',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='people.PeopleTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
