# Generated by Django 2.2.3 on 2019-07-18 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0031_auto_20190718_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicfeaturedarticle',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Page'),
        ),
    ]
