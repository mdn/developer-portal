# Generated by Django 2.2.1 on 2019-06-25 11:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_auto_20190618_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='header_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mozimages.MozImage'),
        ),
    ]
