# Generated by Django 2.2.12 on 2020-05-11 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0011_remove_contentpage_hero_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentpage',
            name='card_image',
            field=models.ForeignKey(blank=True, help_text='An image in 16:9 aspect ratio', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mozimages.MozImage', verbose_name='Image'),
        ),
    ]
